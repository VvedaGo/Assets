using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace CottageGardenDecor.Editor
{
    /// <summary>
    /// Shipping state of the three demo scenes (Э14 release check): the builders create one camera per media shot (Cam_*) and
    /// per-shot cloud groups; the saved scenes must ship with ONE active "Main Camera" (tag MainCamera, AudioListener, URP post on)
    /// and no media-only helpers. Finalize() replaces the shot cameras by that one camera framed like the main shot and removes the
    /// media-only objects, then saves the scene. The builders call it after rendering (media renders keep their own cameras).
    /// </summary>
    public static class CottageGardenDecorSceneFinalize
    {
        private static string Scenes => CottageGardenDecorPackBuilder.Config.DemoDir + "/Scenes";

        [MenuItem("Tools/Cottage Garden Decor/Finalize Demo Scenes (one Main Camera)")]
        public static string FinalizeAll()
        {
            var log = new System.Text.StringBuilder();
            log.AppendLine(Finalize("Demo_CottageGarden"));
            log.AppendLine(Finalize("Demo_Compositions"));
            log.AppendLine(Finalize("Demo_Catalog"));
            return log.ToString();
        }

        public static string Finalize(string sceneName)
        {
            var scene = EditorSceneManager.OpenScene($"{Scenes}/{sceneName}.unity", OpenSceneMode.Single);
            var root = GameObject.Find(CottageGardenDecorPackBuilder.Config.Tag + "_Demo").transform;
            var cams = Object.FindObjectsByType<Camera>(FindObjectsInactive.Include, FindObjectsSortMode.None);
            var before = cams.Length;
            var template = cams.FirstOrDefault(c => c.name == "Cam_Hero") ?? cams.FirstOrDefault(c => c.name == "Cam_Catalog") ?? cams.FirstOrDefault();

            var main = new GameObject("Main Camera");
            main.tag = "MainCamera";
            var cam = main.AddComponent<Camera>();
            cam.nearClipPlane = 0.3f; cam.farClipPlane = 600;
            if (template != null)
            {
                main.transform.SetPositionAndRotation(template.transform.position, template.transform.rotation);
                cam.fieldOfView = template.fieldOfView; cam.clearFlags = template.clearFlags; cam.backgroundColor = template.backgroundColor;
            }
            if (sceneName == "Demo_Compositions")
            {
                // vignettes are 40 m apart for the shot renders; the shipped scene shows them side by side: each plinth with the
                // group standing on it is moved so the plinths are 2 m apart, then one overview camera frames all of them
                var plinths = root.Cast<Transform>().Where(t => t.name.StartsWith("Plinth_")).OrderBy(t => Bounds(t).center.x).ToList();
                var groups = root.Cast<Transform>().Where(t => t.name.Contains("_Comp_") || t.name.StartsWith("Group_")).ToList();
                var pairs = plinths.Select(pl => (pl, g: groups.OrderBy(t => Mathf.Abs(Bounds(t).center.x - Bounds(pl).center.x)).First())).ToList();
                var x = 0f;
                foreach (var (pl, g) in pairs)
                {
                    var pb = Bounds(pl);
                    var dx = x - pb.min.x;
                    pl.position += new Vector3(dx, 0, 0);
                    g.position += new Vector3(dx, 0, 0);
                    x += pb.size.x + 2f;
                }
                var all = Bounds(root);
                var target = new Vector3(all.center.x, 0.8f, all.center.z);
                var dir = Quaternion.Euler(38, -10, 0) * Vector3.forward;               // 38° down, 10° off the front axis
                cam.fieldOfView = 30; cam.clearFlags = CameraClearFlags.Skybox;
                var dist = all.size.x * 0.5f / Mathf.Tan(Mathf.Deg2Rad * cam.fieldOfView * 0.5f * 16f / 9f) * 1.22f;
                main.transform.position = target - dir * dist;
                main.transform.rotation = Quaternion.LookRotation(dir);
            }
            var data = main.AddComponent<UniversalAdditionalCameraData>();
            data.renderPostProcessing = true;
            data.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            main.AddComponent<AudioListener>();

            foreach (var c in cams) Object.DestroyImmediate(c.gameObject);
            foreach (var l in Object.FindObjectsByType<AudioListener>(FindObjectsInactive.Include, FindObjectsSortMode.None))
                if (l.gameObject != main) Object.DestroyImmediate(l);

            // media-only helpers: per-shot cloud groups of the other shots / empty groups, wireframe overlays
            var removed = new System.Collections.Generic.List<string>();
            foreach (Transform t in root.Cast<Transform>().ToList())
                if (t.name.StartsWith("Clouds_") && (!t.gameObject.activeSelf || t.childCount == 0)) { removed.Add(t.name); Object.DestroyImmediate(t.gameObject); }
            foreach (var w in root.GetComponentsInChildren<Transform>(true).Where(t => t.name == "Wire").ToList()) { removed.Add("Wire"); Object.DestroyImmediate(w.gameObject); }

            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene);
            var after = Object.FindObjectsByType<Camera>(FindObjectsInactive.Include, FindObjectsSortMode.None).Length;
            return $"{sceneName}: cameras {before} -> {after} (Main Camera, tag MainCamera, AudioListener); removed [{string.Join(", ", removed)}]";
        }

        private static Bounds Bounds(Transform t)
        {
            var rs = t.GetComponentsInChildren<Renderer>().Where(r => !(r is ParticleSystemRenderer)).ToArray();
            var b = rs[0].bounds;
            foreach (var r in rs) b.Encapsulate(r.bounds);
            return b;
        }
    }
}
