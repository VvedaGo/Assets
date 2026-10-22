using System.Collections.Generic;
using UnityEngine;

namespace MarketFarm.Editor
{
    /// <summary>A family: base prefab + shared material + the list of variants to generate.</summary>
    [CreateAssetMenu(menuName = "MarketFarm/Variant Set", fileName = "VariantSet")]
    public sealed class MarketVariantSet : ScriptableObject
    {
        [SerializeField] private string _family;
        [SerializeField] private GameObject _basePrefab;
        [SerializeField] private Material _sharedMaterial;
        [SerializeField] private List<MarketVariantPreset> _presets = new List<MarketVariantPreset>();

        public string Family => _family;
        public GameObject BasePrefab => _basePrefab;
        public Material SharedMaterial => _sharedMaterial;
        public IReadOnlyList<MarketVariantPreset> Presets => _presets;
    }
}
