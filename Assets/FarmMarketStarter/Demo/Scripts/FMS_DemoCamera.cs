using UnityEngine;
using UnityEngine.InputSystem;

namespace FarmMarketStarter.Demo
{
    /// <summary>Slow auto-orbit around a target. Drag with the left mouse button to take over, scroll to zoom.</summary>
    public class FMS_DemoCamera : MonoBehaviour
    {
        [SerializeField] private Transform target;
        [SerializeField] private Transform galleryTarget;
        [SerializeField] private float galleryDistance = 7f;
        [SerializeField] private float distance = 7f;
        [SerializeField] private float autoSpeed = 6f;
        [SerializeField] private float dragSpeed = 0.25f;
        [SerializeField] private float minDistance = 2.5f;
        [SerializeField] private float maxDistance = 14f;
        [SerializeField] private float idleResumeSeconds = 3f;

        private float _yaw;
        private float _pitch;
        private float _lastInputTime = -100f;
        private bool _onGallery;
        private Transform _marketTarget;
        private float _marketDistance;
        private float _marketYaw;
        private float _marketPitch;

        private void Start()
        {
            var offset = transform.position - target.position;
            distance = offset.magnitude;
            _yaw = Mathf.Atan2(offset.x, offset.z) * Mathf.Rad2Deg;
            _pitch = Mathf.Asin(offset.y / distance) * Mathf.Rad2Deg;
            _marketTarget = target;
            _marketYaw = _yaw;
            _marketPitch = _pitch;
            _marketDistance = distance;
        }

        private void ToggleGallery()
        {
            _onGallery = !_onGallery;
            target = _onGallery ? galleryTarget : _marketTarget;
            distance = _onGallery ? galleryDistance : _marketDistance;
            _yaw = _onGallery ? 180f : _marketYaw;
            _pitch = _onGallery ? 50f : _marketPitch;
        }

        private void LateUpdate()
        {
            var keyboard = Keyboard.current;
            if (keyboard != null && galleryTarget != null && keyboard.tabKey.wasPressedThisFrame) ToggleGallery();

            var mouse = Mouse.current;
            if (mouse != null)
            {
                if (mouse.leftButton.isPressed)
                {
                    var delta = mouse.delta.ReadValue();
                    _yaw += delta.x * dragSpeed;
                    _pitch = Mathf.Clamp(_pitch - delta.y * dragSpeed, 4f, 70f);
                    _lastInputTime = Time.time;
                }

                var scroll = mouse.scroll.ReadValue().y;
                if (Mathf.Abs(scroll) > 0.01f)
                {
                    distance = Mathf.Clamp(distance - scroll * 0.005f, minDistance, maxDistance);
                    _lastInputTime = Time.time;
                }
            }

            if (!_onGallery && Time.time - _lastInputTime > idleResumeSeconds)
                _yaw += autoSpeed * Time.deltaTime;

            var rotation = Quaternion.Euler(-_pitch, _yaw, 0f);
            transform.position = target.position + rotation * new Vector3(0f, 0f, distance);
            transform.LookAt(target.position);
        }
    }
}
