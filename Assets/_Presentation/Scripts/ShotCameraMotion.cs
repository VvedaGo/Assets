using UnityEngine;

namespace FarmAnimals.Presentation
{
    /// <summary>
    /// Presentation only. Slow camera move for the videos: orbits around Target from YawFrom to YawTo degrees (relative
    /// to the authored position) and dollies by Dolly (fraction of the distance, + = closer) over Seconds, eased.
    /// Runs in Update, so the ShotRecorder (LateUpdate) captures the moved camera.
    /// </summary>
    public sealed class ShotCameraMotion : MonoBehaviour
    {
        public Vector3 Target;
        public float YawFrom = -8f, YawTo = 8f, Dolly = 0.08f, Seconds = 10f;

        private Vector3 _offset;
        private float _t0;

        private void Start()
        {
            _offset = transform.position - Target;
            _t0 = Time.time;
            Apply(0f);
        }

        private void Update() => Apply(Mathf.Clamp01((Time.time - _t0) / Seconds));

        private void Apply(float t)
        {
            var e = t * t * (3f - 2f * t);                                  // smoothstep: soft start and stop
            var yaw = Mathf.Lerp(YawFrom, YawTo, e);
            var offset = Quaternion.Euler(0f, yaw, 0f) * _offset * (1f - Dolly * e);
            transform.position = Target + offset;
            transform.LookAt(Target);
        }
    }
}
