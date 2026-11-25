using System.Collections;
using UnityEngine;

namespace FarmAnimals.Demo
{
    /// <summary>
    /// Demo behaviour for the showcase scenes (not needed in a game). Drives the pack's Animator Controller through its
    /// parameters: "Speed" (Locomotion blend tree) and one bool per extra clip (Graze, Lie_Idle, Sit_Idle...).
    /// Cycle: plays idle, walk, run and every extra clip in turn, in place. Wander: walks to random points around the
    /// start position (moving the transform at the clip's speed), pausing with idle or an extra clip in between.
    /// Hold: keeps one action (Idle, Walk, Fast or an extra clip). Patrol: holds the action and walks forward and back
    /// along its facing over a fixed length. Every animal starts at a random phase so herds do not move in sync.
    /// </summary>
    [RequireComponent(typeof(Animator))]
    public sealed class FarmAnimalDemo : MonoBehaviour
    {
        public enum DemoMode { Cycle, Wander, Hold, Patrol }

        private static readonly int SpeedId = Animator.StringToHash("Speed");

        [SerializeField] private DemoMode _mode = DemoMode.Cycle;
        [Tooltip("Seconds each action is shown.")]
        [SerializeField] private float _actionTime = 4f;
        [Tooltip("Bool parameters of the extra clips (filled by the demo builder from the controller).")]
        [SerializeField] private string[] _extraClips = new string[0];
        [Tooltip("True when the controller has a Locomotion blend tree driven by Speed.")]
        [SerializeField] private bool _hasLocomotion;
        [Tooltip("Speed of the walk clip in m/s (Locomotion threshold).")]
        [SerializeField] private float _walkSpeed = 0.5f;
        [Tooltip("Speed of the faster clip (Run/Trot) in m/s; 0 = none.")]
        [SerializeField] private float _fastSpeed;
        [Tooltip("Wander: radius around the start position, metres.")]
        [SerializeField] private float _wanderRadius = 1.5f;
        [Tooltip("Hold/Patrol: Idle, Walk, Fast or the name of an extra clip.")]
        [SerializeField] private string _holdAction = "Idle";
        [Tooltip("Patrol: distance walked before turning back, metres.")]
        [SerializeField] private float _patrolLength = 1.5f;
        [Tooltip("Patrol: speed for an extra clip (Swim, Crawl...), m/s.")]
        [SerializeField] private float _moveSpeed = 0.25f;
        [Tooltip("Local direction the model faces (the pack models face +Z).")]
        [SerializeField] private Vector3 _localForward = Vector3.forward;

        private Animator _animator;
        private Vector3 _home;

        private void Awake()
        {
            _animator = GetComponent<Animator>();
            _home = transform.position;
        }

        private void Start()
        {
            var state = _animator.GetCurrentAnimatorStateInfo(0);
            _animator.Play(state.fullPathHash, 0, Random.value);          // random phase
            _animator.speed = Random.Range(0.92f, 1.08f);
            switch (_mode)
            {
                case DemoMode.Wander when _hasLocomotion: StartCoroutine(WanderLoop()); break;
                case DemoMode.Hold: Apply(_holdAction); break;
                case DemoMode.Patrol: StartCoroutine(PatrolLoop()); break;
                default: StartCoroutine(CycleLoop()); break;
            }
        }

        private IEnumerator CycleLoop()
        {
            var count = 1 + (_hasLocomotion ? 1 : 0) + (_fastSpeed > 0f ? 1 : 0) + _extraClips.Length;
            var step = Random.Range(0, count);
            while (true)
            {
                var i = step % count;
                ResetParameters();
                if (i == 1 && _hasLocomotion) _animator.SetFloat(SpeedId, _walkSpeed);
                else if (i == 2 && _fastSpeed > 0f) _animator.SetFloat(SpeedId, _fastSpeed);
                else if (i > 0)
                {
                    var extra = i - 1 - (_hasLocomotion ? 1 : 0) - (_fastSpeed > 0f ? 1 : 0);
                    if (extra >= 0) _animator.SetBool(_extraClips[extra], true);
                }
                step++;
                yield return new WaitForSeconds(_actionTime * Random.Range(0.8f, 1.2f));
            }
        }

        private IEnumerator WanderLoop()
        {
            while (true)
            {
                ResetParameters();
                if (_extraClips.Length > 0 && Random.value < 0.5f)
                    _animator.SetBool(_extraClips[Random.Range(0, _extraClips.Length)], true);
                yield return new WaitForSeconds(_actionTime * Random.Range(0.6f, 1.4f));

                ResetParameters();
                var target = _home + Quaternion.Euler(0f, Random.Range(0f, 360f), 0f) * Vector3.forward * Random.Range(0.3f, 1f) * _wanderRadius;
                target.y = _home.y;
                _animator.SetFloat(SpeedId, _walkSpeed);
                while (Vector3.Distance(transform.position, target) > 0.05f)
                {
                    var to = target - transform.position; to.y = 0f;
                    var face = Quaternion.LookRotation(to) * Quaternion.Inverse(Quaternion.LookRotation(_localForward));
                    transform.rotation = Quaternion.RotateTowards(transform.rotation, face, 120f * Time.deltaTime);
                    var forward = transform.rotation * _localForward;
                    var aligned = Mathf.Clamp01(Vector3.Dot(forward.normalized, to.normalized));
                    transform.position = Vector3.MoveTowards(transform.position, target, _walkSpeed * aligned * Time.deltaTime);
                    yield return null;
                }
            }
        }

        private void Apply(string action)
        {
            ResetParameters();
            if (action == "Walk" && _hasLocomotion) _animator.SetFloat(SpeedId, _walkSpeed);
            else if (action == "Fast" && _fastSpeed > 0f) _animator.SetFloat(SpeedId, _fastSpeed);
            else if (action != "Idle" && System.Array.IndexOf(_extraClips, action) >= 0) _animator.SetBool(action, true);
        }

        private IEnumerator PatrolLoop()
        {
            var speed = _holdAction == "Walk" ? _walkSpeed : _holdAction == "Fast" ? _fastSpeed : _moveSpeed;
            var start = transform.position;
            var dir = transform.rotation * _localForward; dir.y = 0f; dir.Normalize();
            var end = start + dir * _patrolLength;
            transform.position = start + dir * Random.Range(0f, _patrolLength);   // start somewhere along the line
            var toEnd = true;
            while (true)
            {
                Apply(_holdAction);
                var target = toEnd ? end : start;
                toEnd = !toEnd;
                var to = target - transform.position; to.y = 0f;
                if (to.sqrMagnitude > 1e-4f)
                {
                    var face = Quaternion.LookRotation(to) * Quaternion.Inverse(Quaternion.LookRotation(_localForward));
                    while (Quaternion.Angle(transform.rotation, face) > 1f)           // turn on the spot
                    {
                        transform.rotation = Quaternion.RotateTowards(transform.rotation, face, 150f * Time.deltaTime);
                        yield return null;
                    }
                }
                while (Vector3.Distance(transform.position, target) > 0.02f)
                {
                    transform.position = Vector3.MoveTowards(transform.position, target, speed * Time.deltaTime);
                    yield return null;
                }
                if (_hasLocomotion) { Apply("Idle"); yield return new WaitForSeconds(Random.Range(0.6f, 1.6f)); }
            }
        }

        private void ResetParameters()
        {
            if (_hasLocomotion) _animator.SetFloat(SpeedId, 0f);
            foreach (var clip in _extraClips) _animator.SetBool(clip, false);
        }

        /// <summary>Editor setup for Hold/Patrol.</summary>
        public void ConfigureAction(string action, float patrolLength, float moveSpeed)
        {
            _holdAction = action; _patrolLength = patrolLength; _moveSpeed = moveSpeed;
        }

        /// <summary>Editor setup by the demo builder.</summary>
        public void Configure(DemoMode mode, string[] extraClips, bool hasLocomotion, float walkSpeed, float fastSpeed, float wanderRadius, Vector3 localForward)
        {
            _mode = mode; _extraClips = extraClips; _hasLocomotion = hasLocomotion;
            _walkSpeed = walkSpeed; _fastSpeed = fastSpeed; _wanderRadius = wanderRadius; _localForward = localForward;
        }
    }
}
