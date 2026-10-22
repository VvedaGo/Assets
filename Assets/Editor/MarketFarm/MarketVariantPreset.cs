using UnityEngine;

namespace MarketFarm.Editor
{
    /// <summary>One variant of a base prefab: a UV window (_BaseMap_ST) on the shared atlas.</summary>
    [CreateAssetMenu(menuName = "MarketFarm/Variant Preset", fileName = "VariantPreset")]
    public sealed class MarketVariantPreset : ScriptableObject
    {
        [SerializeField] private string _variantName;
        [Tooltip("xy = tiling, zw = offset (Unity _BaseMap_ST).")]
        [SerializeField] private Vector4 _baseMapST = new Vector4(1f, 1f, 0f, 0f);
        [Tooltip("Optional: replaces the family's base material (e.g. cloth colour).")]
        [SerializeField] private Material _materialOverride;
        [SerializeField] private string _addressableLabel;

        public string VariantName => _variantName;
        public Vector4 BaseMapST => _baseMapST;
        public Material MaterialOverride => _materialOverride;
        public string AddressableLabel => _addressableLabel;
    }
}
