using System;
using UnityEngine;

namespace FarmAnimals
{
    /// <summary>
    /// Receives the AnimationEvents baked into the Farm Animals clips and re-raises them as C# events, so game code can
    /// play footstep, wing or animal sounds without editing the clips. The pack ships no sounds.
    /// Event names in the clips: Footstep (parameter = leg, e.g. "FrontL"), Vocal, LayEgg, Peck, Nibble, Sniff, Paw,
    /// Pounce, Jump, Land, Takeoff, Flap, WingFlap, Paddle, Curl, Display.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class FarmAnimalEvents : MonoBehaviour
    {
        /// <summary>Raised on every paw or hoof contact; the argument names the leg.</summary>
        public event Action<string> FootstepRaised;

        /// <summary>Raised at the moment of a call (moo, bark, crow).</summary>
        public event Action<string> VocalRaised;

        /// <summary>Raised on the egg frame of a laying clip.</summary>
        public event Action<string> EggLaid;

        /// <summary>Every clip event: (event name, string parameter). Includes the three above.</summary>
        public event Action<string, string> AnimationEventRaised;

        // Called by AnimationEvents (name-matched by Unity).
        private void Footstep(string leg) { FootstepRaised?.Invoke(leg); Raise(nameof(Footstep), leg); }
        private void Vocal(string call) { VocalRaised?.Invoke(call); Raise(nameof(Vocal), call); }
        private void LayEgg(string tag) { EggLaid?.Invoke(tag); Raise(nameof(LayEgg), tag); }
        private void Peck(string p) => Raise(nameof(Peck), p);
        private void Nibble(string p) => Raise(nameof(Nibble), p);
        private void Sniff(string p) => Raise(nameof(Sniff), p);
        private void Paw(string p) => Raise(nameof(Paw), p);
        private void Pounce(string p) => Raise(nameof(Pounce), p);
        private void Jump(string p) => Raise(nameof(Jump), p);
        private void Land(string p) => Raise(nameof(Land), p);
        private void Takeoff(string p) => Raise(nameof(Takeoff), p);
        private void Flap(string p) => Raise(nameof(Flap), p);
        private void WingFlap(string p) => Raise(nameof(WingFlap), p);
        private void Paddle(string p) => Raise(nameof(Paddle), p);
        private void Curl(string p) => Raise(nameof(Curl), p);
        private void Display(string p) => Raise(nameof(Display), p);

        private void Raise(string name, string parameter) => AnimationEventRaised?.Invoke(name, parameter);
    }
}
