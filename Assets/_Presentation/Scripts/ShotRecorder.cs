using System.IO;
using UnityEngine;

namespace FarmAnimals.Presentation
{
    /// <summary>
    /// Presentation only (not part of any pack). In Play mode renders the camera every frame at a fixed frame rate
    /// (Time.captureFramerate, so the result does not depend on how fast the editor renders) and writes JPG frames to
    /// OutputDir, then leaves Play mode. Encode with ffmpeg: ffmpeg -framerate 30 -i f_%05d.jpg -pix_fmt yuv420p out.mp4
    /// </summary>
    [RequireComponent(typeof(Camera))]
    public sealed class ShotRecorder : MonoBehaviour
    {
        public string OutputDir = "";
        public int Width = 1920, Height = 1080, Fps = 30;
        public float Seconds = 8f, WarmupSeconds = 1f;
        public bool StopPlayModeWhenDone = true;

        private Camera _camera;
        private RenderTexture _rt;
        private Texture2D _frame;
        private int _index, _warmup, _total;

        private void Start()
        {
            _camera = GetComponent<Camera>();
            Time.captureFramerate = Fps;
            _rt = new RenderTexture(Width, Height, 24) { antiAliasing = 8 };
            _frame = new Texture2D(Width, Height, TextureFormat.RGB24, false);
            _warmup = Mathf.RoundToInt(WarmupSeconds * Fps);
            _total = Mathf.RoundToInt(Seconds * Fps);
            Directory.CreateDirectory(OutputDir);
            foreach (var f in Directory.GetFiles(OutputDir, "f_*.jpg")) File.Delete(f);
        }

        private void LateUpdate()
        {
            if (_warmup-- > 0) return;                                   // let random phases and walkers settle
            var old = _camera.targetTexture;
            _camera.targetTexture = _rt;
            _camera.aspect = Width / (float)Height;
            _camera.Render();
            _camera.targetTexture = old;
            RenderTexture.active = _rt;
            _frame.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
            RenderTexture.active = null;
            File.WriteAllBytes(Path.Combine(OutputDir, $"f_{_index:00000}.jpg"), _frame.EncodeToJPG(95));
            if (++_index < _total) return;

            Time.captureFramerate = 0;
            File.WriteAllText(Path.Combine(OutputDir, "done.txt"), _index.ToString());
            enabled = false;
#if UNITY_EDITOR
            if (StopPlayModeWhenDone) UnityEditor.EditorApplication.isPlaying = false;
#endif
        }

        private void OnDestroy()
        {
            if (_rt != null) Destroy(_rt);
            if (_frame != null) Destroy(_frame);
        }
    }
}
