using System.Collections.Generic;
using System.Text.RegularExpressions;
using UnityEngine;

namespace MarketFarm.Editor
{
    public readonly struct MarketModelStats
    {
        public readonly string Name;
        public readonly int Lod0Tris;
        public readonly int MaterialCount;
        public readonly float MinY;
        public readonly Vector2 UvMin;
        public readonly Vector2 UvMax;
        public readonly bool HasCollider;
        public readonly bool HasLodGroup;

        public MarketModelStats(string name, int lod0Tris, int materialCount, float minY,
            Vector2 uvMin, Vector2 uvMax, bool hasCollider, bool hasLodGroup)
        {
            Name = name;
            Lod0Tris = lod0Tris;
            MaterialCount = materialCount;
            MinY = minY;
            UvMin = uvMin;
            UvMax = uvMax;
            HasCollider = hasCollider;
            HasLodGroup = hasLodGroup;
        }
    }

    /// <summary>Pure rules from docs/MarketFarm_Expansion_Plan.md §0 — no asset access, unit-testable.</summary>
    public static class MarketFarmRules
    {
        public const int SmallPropTris = 600;
        public const int CrateTris = 1000;
        public const int LargeTris = 3000;
        public const float PivotTolerance = 0.02f;

        private static readonly Regex NamePattern = new Regex(@"^[A-Z][A-Za-z0-9]*(_[A-Za-z0-9]+)+$");
        private static readonly Regex VariantPattern = new Regex(@"^[A-Z][A-Za-z0-9]*$");
        private static readonly string[] LargePrefixes = { "Crate_Stack", "HayBale_Stack", "StreetStall", "Table", "Cart", "Canopy", "Barn", "Farmhouse", "G_" };

        // Explicit budgets from the plan (§2) override the size class.
        private static readonly Dictionary<string, int> Overrides = new Dictionary<string, int>
        {
            { "Sack_Standing", 480 }, { "Sack_OpenTop", 520 }, { "Sack_Lying", 480 }, { "Sack_Pile", 1100 },
            { "Hay_Loose", 300 },
        };

        public static bool IsValidName(string name) => NamePattern.IsMatch(name);

        public static int TriBudget(string name)
        {
            if (Overrides.TryGetValue(name, out var budget)) return budget;
            if (name.StartsWith("Crate_Fill_")) return 400;
            foreach (var prefix in LargePrefixes)
                if (name.StartsWith(prefix)) return LargeTris;
            return name.StartsWith("Crate_") ? CrateTris : SmallPropTris;
        }

        public static List<string> Check(MarketModelStats s)
        {
            var issues = new List<string>();
            if (!IsValidName(s.Name)) issues.Add($"name '{s.Name}' breaks Family_Part convention");

            var budget = TriBudget(s.Name);
            if (s.Lod0Tris > budget) issues.Add($"LOD0 {s.Lod0Tris} tris > budget {budget}");

            if (s.MaterialCount > 2 && budget <= SmallPropTris) issues.Add($"{s.MaterialCount} materials on a small prop (max 2)");
            if (Mathf.Abs(s.MinY) > PivotTolerance) issues.Add($"pivot not at base: min Y = {s.MinY:F3}");
            if (!s.HasLodGroup) issues.Add("no LOD0-2");
            if (!s.HasCollider) issues.Add("no collider");
            if (s.UvMin.x < 0f || s.UvMin.y < 0f || s.UvMax.x > 1f || s.UvMax.y > 1f)
                issues.Add($"UV outside 0..1: {s.UvMin}..{s.UvMax}");
            return issues;
        }

        public static List<string> CheckPreset(string variantName, Vector4 st)
        {
            var issues = new List<string>();
            if (string.IsNullOrWhiteSpace(variantName)) issues.Add("empty variant name");
            else if (!VariantPattern.IsMatch(variantName)) issues.Add($"variant name '{variantName}' must be PascalCase without separators");
            if (st.x <= 0f || st.y <= 0f) issues.Add($"tiling must be > 0: ({st.x}, {st.y})");
            if (st.z < 0f || st.w < 0f || st.z + st.x > 1.0001f || st.w + st.y > 1.0001f)
                issues.Add($"UV window leaves 0..1: {st}");
            return issues;
        }

        public static string VariantPrefabName(string family, string variant) => $"P_{family}_{variant}";
        public static string VariantMaterialName(string family, string variant) => $"M_{family}_{variant}";
    }
}
