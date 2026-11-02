using NUnit.Framework;
using UnityEngine;

namespace MarketFarm.Editor.Tests
{
    public class MarketFarmRulesTests
    {
        private static MarketModelStats Stats(string name, int tris = 100, int mats = 1, float minY = 0f,
            float uvMax = 1f, bool collider = true, bool lod = true) =>
            new MarketModelStats(name, tris, mats, minY, Vector2.zero, new Vector2(uvMax, uvMax), collider, lod);

        [TestCase("Sack_Standing", 480)]
        [TestCase("Sack_Pile", 1100)]
        [TestCase("Crate_Fill_Potato", 400)]
        [TestCase("Crate_Base", 1000)]
        [TestCase("Crate_Stack", 3000)]
        [TestCase("Barrel_Standing", 600)]
        public void TriBudget_MatchesPlan(string name, int expected) =>
            Assert.AreEqual(expected, MarketFarmRules.TriBudget(name));

        [Test]
        public void Check_ValidModel_NoIssues() =>
            Assert.IsEmpty(MarketFarmRules.Check(Stats("Sack_Standing", tris: 480)));

        [Test]
        public void Check_OverBudgetByOne_Reported() =>
            Assert.AreEqual(1, MarketFarmRules.Check(Stats("Sack_Standing", tris: 481)).Count);

        [Test]
        public void Check_RaisedPivot_Reported() =>
            Assert.AreEqual(1, MarketFarmRules.Check(Stats("Sack_Standing", minY: 0.05f)).Count);

        [Test]
        public void Check_UvOutsideRange_Reported() =>
            Assert.AreEqual(1, MarketFarmRules.Check(Stats("Sack_Standing", uvMax: 1.2f)).Count);

        [Test]
        public void Check_MissingColliderAndLod_BothReported() =>
            Assert.AreEqual(2, MarketFarmRules.Check(Stats("Sack_Standing", collider: false, lod: false)).Count);

        [Test]
        public void Check_ThreeMaterialsOnSmallProp_Reported() =>
            Assert.AreEqual(1, MarketFarmRules.Check(Stats("Sack_Standing", mats: 3)).Count);

        [TestCase("sack_standing")]
        [TestCase("Sack")]
        [TestCase("Sack Standing")]
        public void IsValidName_BadNames_False(string name) => Assert.IsFalse(MarketFarmRules.IsValidName(name));

        [Test]
        public void CheckPreset_WindowInsideAtlas_Valid() =>
            Assert.IsEmpty(MarketFarmRules.CheckPreset("Potato", new Vector4(0.0625f, 0.0625f, 0.6875f, 0.375f)));

        [Test]
        public void CheckPreset_WindowLeavesAtlas_Reported() =>
            Assert.IsNotEmpty(MarketFarmRules.CheckPreset("Potato", new Vector4(0.5f, 0.5f, 0.75f, 0f)));

        [Test]
        public void CheckPreset_ZeroTiling_Reported() =>
            Assert.IsNotEmpty(MarketFarmRules.CheckPreset("Potato", new Vector4(0f, 1f, 0f, 0f)));

        [Test]
        public void Names_FollowConvention()
        {
            Assert.AreEqual("P_Sack_Potato", MarketFarmRules.VariantPrefabName("Sack", "Potato"));
            Assert.AreEqual("M_Sack_Potato", MarketFarmRules.VariantMaterialName("Sack", "Potato"));
        }
    }
}
