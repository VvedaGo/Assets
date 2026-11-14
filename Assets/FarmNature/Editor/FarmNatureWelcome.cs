#if UNITY_EDITOR
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FarmNature.Editor
{
    public sealed class FarmNatureWelcome : EditorWindow
    {
        private const string Root = "Assets/FarmNature";
        private const string Scene = Root + "/Demo/Scenes/Demo_FarmNature_Showcase.unity";

        [MenuItem("Tools/Farm Nature/Getting Started", priority = 0)]
        public static void Open()
        {
            var window = GetWindow<FarmNatureWelcome>("Farm Nature");
            window.minSize = new Vector2(430, 390);
            window.Show();
        }

        private void OnGUI()
        {
            GUILayout.Space(15);
            GUILayout.Label("FARM NATURE", new GUIStyle(EditorStyles.boldLabel) { fontSize = 27 });
            GUILayout.Label("1.0.0  |  Crops, Trees & Landscape", EditorStyles.miniLabel);
            GUILayout.Space(15);
            EditorGUILayout.HelpBox("88 individual art prefabs, one organized showcase scene and six scene studies. Materials target Universal Render Pipeline.", MessageType.Info);
            if (GUILayout.Button("Open Showcase Scene", GUILayout.Height(34)))
            {
                if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
                {
                    EditorSceneManager.OpenScene(Scene);
                    Frame("01_Overview");
                }
            }
            GUILayout.Space(8);
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Overview")) Frame("01_Overview");
            if (GUILayout.Button("Scene Studies")) Frame("02_SceneStudies");
            if (GUILayout.Button("Collection")) Frame("03_AssetCollection");
            EditorGUILayout.EndHorizontal();
            if (GUILayout.Button("Browse Art Prefabs")) Select(Root + "/Art/Prefabs");
            if (GUILayout.Button("Open Documentation")) Application.OpenURL("file:///" + Path.GetFullPath(Root + "/Documentation/README.md").Replace('\\', '/'));
            if (GUILayout.Button("Select Demo URP Settings")) Select(Root + "/Demo/Settings/FarmNature_DemoPipeline.asset");
            GUILayout.Space(12);
            EditorGUILayout.HelpBox("Already using URP? Keep your own pipeline. In a new project, assign the included demo pipeline in Project Settings > Graphics and the active Quality level. This window never changes your project's graphics settings automatically.", MessageType.None);
            EditorGUILayout.SelectableLabel("Support: sergvved@gmail.com", EditorStyles.miniLabel, GUILayout.Height(20));
        }

        private static void Select(string path)
        {
            var asset = AssetDatabase.LoadMainAssetAtPath(path);
            if (asset == null) return;
            Selection.activeObject = asset;
            EditorGUIUtility.PingObject(asset);
        }

        private static void Frame(string name)
        {
            var go = UnityEngine.SceneManagement.SceneManager.GetActiveScene().GetRootGameObjects().FirstOrDefault(x => x.name == name);
            if (go == null) return;
            Selection.activeGameObject = go;
            var view = SceneView.lastActiveSceneView ?? GetWindow<SceneView>();
            view.FrameSelected();
        }
    }
}
#endif
