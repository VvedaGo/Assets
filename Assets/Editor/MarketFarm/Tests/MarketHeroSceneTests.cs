using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace MarketFarm.Editor.Tests
{
    /// <summary>Rebuilds MarketHero.unity and checks it: pack-only prefabs, no missing/pink content, deterministic layout.</summary>
    public class MarketHeroSceneTests
    {
        private const string PackPrefabs = "Assets/FarmMarketStarter/Art/Prefabs/";

        [OneTimeSetUp]
        public void BuildOnce() => MarketHeroBuilder.Build();

        private static IEnumerable<GameObject> AllObjects() =>
            EditorSceneManager.GetActiveScene().GetRootGameObjects().SelectMany(r => r.GetComponentsInChildren<Transform>(true)).Select(t => t.gameObject);

        [Test]
        public void EveryPrefabInstance_BelongsToThePack()
        {
            var instances = AllObjects().Where(PrefabUtility.IsAnyPrefabInstanceRoot).ToList();
            Assert.IsNotEmpty(instances);
            foreach (var go in instances)
            {
                var source = PrefabUtility.GetCorrespondingObjectFromOriginalSource(go);
                var path = AssetDatabase.GetAssetPath(source);
                Assert.IsTrue(path.StartsWith(PackPrefabs), $"{go.name} comes from {path}, not from the pack");
            }
        }

        [Test]
        public void Scene_HasNoMissingScriptsMeshesOrPinkMaterials()
        {
            foreach (var go in AllObjects())
            {
                Assert.AreEqual(0, GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(go), $"missing script on {go.name}");
                var filter = go.GetComponent<MeshFilter>();
                if (filter != null) Assert.IsNotNull(filter.sharedMesh, $"missing mesh on {go.name}");
                var renderer = go.GetComponent<Renderer>();
                if (renderer == null) continue;
                Assert.IsNotEmpty(renderer.sharedMaterials, $"no materials on {go.name}");
                foreach (var m in renderer.sharedMaterials)
                {
                    Assert.IsNotNull(m, $"missing material on {go.name}");
                    Assert.IsNotNull(m.shader, $"{m.name} has no shader");
                    Assert.IsFalse(m.shader.name.Contains("InternalErrorShader"), $"{m.name} renders pink");
                    Assert.IsTrue(m.shader.isSupported, $"{m.name}: shader {m.shader.name} is not supported");
                }
            }
        }

        [Test]
        public void AllUsedPrefabs_ExistInThePack()
        {
            var pack = MarketHeroBuilder.AllPackPrefabNames();
            foreach (var used in MarketHeroBuilder.UsedPrefabs) CollectionAssert.Contains(pack, used);
        }

        [Test]
        public void Build_IsDeterministic()
        {
            var first = Fingerprint();
            MarketHeroBuilder.Build();
            Assert.AreEqual(first, Fingerprint());
        }

        // Name + rounded transform of everything under the diorama.
        private static string Fingerprint() =>
            string.Join("|", AllObjects()
                .Where(g => g.transform.root.name == MarketHeroBuilder.RootName)
                .Select(g => $"{g.name}@{g.transform.position:F3}/{g.transform.rotation.eulerAngles:F2}/{g.transform.lossyScale:F3}"));
    }
}
