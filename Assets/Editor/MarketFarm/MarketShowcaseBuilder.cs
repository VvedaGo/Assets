using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace MarketFarm.Editor
{
    /// <summary>Asset Store catalogue scene: every Base prefab and Group in a labelled grid on a studio backdrop.</summary>
    public static class MarketShowcaseBuilder
    {
        private const string ScenePath = "Assets/Scenes/MarketShowcase.unity";

        private static readonly (string Title, string[] Items)[] Rows =
        {
            ("STALLS & FURNITURE", new[] { "StreetStall", "Canopy_Green", "Table_Cloth", "Shelf_CheeseBread", "Cart", "Wheelbarrow" }),
            ("CRATES", new[] { "Crate_Empty", "Crate_Tomato", "Crate_AppleRed", "Crate_AppleGreen", "Crate_Carrot", "Crate_Pumpkin", "Crate_Stack" }),
            ("SACKS & BASKETS", new[] { "Sack_Empty", "Sack_Bundle", "Sack_Flour", "Sack_Grain", "Sack_Groats", "Basket_Small", "Basket_Round", "Basket_Rect" }),
            ("BARRELS & HAY", new[] { "Barrel_Small", "Barrel_Standing", "Barrel_Tap", "HayBale_1", "HayBale_2", "HayBale_Stack" }),
            ("FENCES, LIGHTS & TOOLS", new[] { "Fence_Straight", "Fence_Corner", "Fence_Gate", "LanternPost", "Lantern", "Sign_Chalkboard", "Scale_Weights", "Tool_Pitchfork", "Tool_Rake", "Tool_Shovel" }),
            ("READY-MADE GROUPS", new[] { "G_CrateStack", "G_SackPile", "G_HayStack", "G_BarrelRow", "G_TableDisplay", "G_StallFront", "G_FarmCorner", "G_CartLoad" }),
        };

        private static readonly Color Backdrop = new Color(0.80f, 0.84f, 0.88f);
        private const float ItemGap = 0.9f;
        private const float RowGap = 2.4f;

        [MenuItem("Tools/MarketFarm/Build Showcase Scene")]
        public static void Build()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var stage = new GameObject("Showcase").transform;
            var extent = BuildGrid(stage);
            BuildStudio(stage, extent);
            EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(), ScenePath);
            Debug.Log($"[MarketFarm] showcase built: {ScenePath}");
        }

        public static void BuildAndShoot()
        {
            Build();
            var dir = System.Environment.GetEnvironmentVariable("MARKET_SHOTS");
            if (string.IsNullOrEmpty(dir)) throw new System.InvalidOperationException("MARKET_SHOTS is not set");
            Directory.CreateDirectory(dir);
            var cam = Camera.main.transform;
            MarketSceneBuilder.Shoot(Path.Combine(dir, "showcase_4k.png"), cam.position, cam.position + cam.forward, Camera.main.fieldOfView, 3840, 2160);
        }

        // Returns the footprint (width, depth) of the whole grid, centred on the origin.
        private static Vector2 BuildGrid(Transform parent)
        {
            var rows = new List<(string title, List<(GameObject prefab, Bounds b)> items)>();
            foreach (var (title, names) in Rows)
            {
                var items = new List<(GameObject, Bounds)>();
                foreach (var n in names)
                {
                    var prefab = Load(n);
                    items.Add((prefab, Measure(prefab)));
                }
                rows.Add((title, items));
            }

            var widths = rows.Select(r => r.items.Sum(i => Mathf.Max(i.b.size.x, i.b.size.z)) + ItemGap * (r.items.Count - 1)).ToArray();
            var depths = rows.Select(r => r.items.Max(i => i.b.size.z)).ToArray();
            var totalWidth = widths.Max();
            var totalDepth = depths.Sum() + RowGap * (rows.Count - 1);

            var z = totalDepth / 2f;
            for (var r = 0; r < rows.Count; r++)
            {
                z -= depths[r] / 2f;
                var x = -widths[r] / 2f;
                foreach (var (prefab, b) in rows[r].items)
                {
                    var slot = Mathf.Max(b.size.x, b.size.z);
                    var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, parent);
                    go.transform.position = new Vector3(x + slot / 2f, 0f, z);
                    // Centre the bounds in its slot (pivots are at the base, not always the centre).
                    go.transform.position -= new Vector3(b.center.x, 0f, b.center.z - 0f);
                    go.transform.position += new Vector3(0f, 0.06f, 0f);
                    AddPedestal(parent, new Vector3(x + slot / 2f, 0f, z), slot);
                    AddLabel(parent, prefab.name.StartsWith("P_") ? prefab.name.Substring(2) : prefab.name,
                        new Vector3(x + slot / 2f, 0.07f, z - depths[r] / 2f - 0.3f), 0.02f);
                    x += slot + ItemGap;
                }
                AddLabel(parent, rows[r].title, new Vector3(-widths[r] / 2f - 1.0f, 0.07f, z), 0.034f, TextAnchor.MiddleRight);
                z -= depths[r] / 2f + RowGap;
            }
            return new Vector2(totalWidth, totalDepth);
        }

        private static GameObject Load(string name)
        {
            var path = name.StartsWith("G_") ? $"{MarketSceneBuilder.GroupDir}/{name}.prefab" : $"{MarketSceneBuilder.BaseDir}/P_{name}.prefab";
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (prefab == null) throw new System.InvalidOperationException($"Missing prefab {path} — run Build Demo Market first");
            return prefab;
        }

        private static Bounds Measure(GameObject prefab)
        {
            var instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
            var renderers = instance.GetComponentsInChildren<Renderer>();
            var b = renderers[0].bounds;
            foreach (var r in renderers) b.Encapsulate(r.bounds);
            Object.DestroyImmediate(instance);
            return b;
        }

        private static void AddPedestal(Transform parent, Vector3 center, float slot)
        {
            var disc = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            disc.name = "Pedestal";
            disc.transform.SetParent(parent, false);
            var diameter = slot * 1.12f + 0.15f;
            disc.transform.position = center + new Vector3(0f, 0.03f, 0f);
            disc.transform.localScale = new Vector3(diameter, 0.03f, diameter);
            disc.GetComponent<Renderer>().sharedMaterial = MarketSceneBuilder.FlatMaterial("M_Showcase_Pedestal", new Color(0.93f, 0.91f, 0.87f), 0.25f);
            Object.DestroyImmediate(disc.GetComponent<Collider>());
        }

        private static void AddLabel(Transform parent, string text, Vector3 pos, float size, TextAnchor anchor = TextAnchor.UpperCenter)
        {
            var go = new GameObject($"Label_{text}");
            go.transform.SetParent(parent, false);
            go.transform.position = pos;
            go.transform.rotation = Quaternion.Euler(65f, 0f, 0f);
            var tm = go.AddComponent<TextMesh>();
            tm.text = text.Replace('_', ' ');
            tm.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            go.GetComponent<MeshRenderer>().sharedMaterial = tm.font.material;
            tm.fontSize = 96;
            tm.characterSize = size;
            tm.anchor = anchor;
            tm.alignment = TextAlignment.Left;
            tm.color = new Color(0.20f, 0.22f, 0.26f);
        }

        private static void BuildStudio(Transform parent, Vector2 extent)
        {
            var floor = GameObject.CreatePrimitive(PrimitiveType.Plane);
            floor.name = "Floor";
            floor.transform.SetParent(parent, false);
            floor.transform.localScale = new Vector3(40f, 1f, 40f);
            floor.GetComponent<Renderer>().sharedMaterial = MarketSceneBuilder.FlatMaterial("M_Showcase_Floor", new Color(0.86f, 0.87f, 0.88f), 0.05f);
            Object.DestroyImmediate(floor.GetComponent<Collider>());

            var sun = new GameObject("Key Light").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.color = new Color(1f, 0.96f, 0.9f);
            sun.intensity = 1.5f;
            sun.shadows = LightShadows.Soft;
            sun.shadowStrength = 0.55f;
            sun.transform.rotation = Quaternion.Euler(52f, -28f, 0f);

            RenderSettings.skybox = null;
            RenderSettings.sun = sun;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.78f, 0.84f, 0.92f);
            RenderSettings.ambientEquatorColor = new Color(0.70f, 0.70f, 0.70f);
            RenderSettings.ambientGroundColor = new Color(0.55f, 0.52f, 0.48f);
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = Backdrop;
            RenderSettings.fogStartDistance = 90f;
            RenderSettings.fogEndDistance = 260f;

            var volume = new GameObject("Global Volume").AddComponent<Volume>();
            volume.isGlobal = true;
            volume.sharedProfile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(MarketSceneBuilder.VolumeProfilePath);

            // Fit the whole grid into a 16:9 frame at a gentle downward angle.
            var cam = new GameObject("Main Camera") { tag = "MainCamera" }.AddComponent<Camera>();
            cam.fieldOfView = 28f;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = Backdrop;
            cam.gameObject.AddComponent<AudioListener>();
            var data = cam.GetUniversalAdditionalCameraData();
            data.renderPostProcessing = true;
            data.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;

            var pitch = 42f;
            var halfH = Mathf.Tan(cam.fieldOfView * Mathf.Deg2Rad / 2f);
            var halfW = halfH * 16f / 9f;
            var distance = Mathf.Max((extent.x + 6f) / 2f / halfW, extent.y / 2f / halfH * 0.9f) * 1.18f;
            var dir = Quaternion.Euler(pitch, 0f, 0f) * Vector3.back * -1f; // from the target towards the camera, rotated up
            cam.transform.position = new Vector3(0f, 0.6f + Mathf.Sin(pitch * Mathf.Deg2Rad) * distance, -1.8f - Mathf.Cos(pitch * Mathf.Deg2Rad) * distance);
            cam.transform.LookAt(new Vector3(0f, 0.6f, -1.8f));
        }
    }
}
