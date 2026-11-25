using System.Collections.Generic;
using System.IO;
using System.Linq;
using FarmAnimals.Demo;
using FarmAnimals.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace FarmAnimals.Editor
{
    /// <summary>
    /// Presentation shots for the store media and videos (production tool, nothing here ships in the pack).
    /// One scene per shot in Assets/_Presentation/Scenes: a floating island in the series style, animals of the pack and
    /// set dressing borrowed from Farm Yard / Farm Nature (Assets/_Presentation), a Main Camera with a ShotRecorder.
    /// Layouts follow planning/FarmAnimals/store-preview-references/README.md. Camera space: x right, z away from the
    /// camera, y up, metres; yaw 0 = the model faces +z (away), 180 = faces the camera.
    /// </summary>
    public static class FarmAnimalsShots
    {
        private const string SceneDir = "Assets/_Presentation/Scenes";
        private const string MeshDir = "Assets/_Presentation/Meshes";
        private const string MediaDir = "AssetStore/FarmAnimals/Media/Renders";

        public sealed class It
        {
            public string Name; public Vector3 P; public float Yaw; public float Scale = 1f;
            public string Action = "Idle";                      // Idle, Walk, Fast or an extra clip (animals)
            public FarmAnimalDemo.DemoMode Mode = FarmAnimalDemo.DemoMode.Hold;
            public float Patrol = 1.2f; public float Phase = -1f; public bool Swim;
        }

        public sealed class Shot
        {
            public string Name; public float Mm = 50f; public Vector3 Cam, Look; public float Rx = 7f, Rz = 6f;
            public float Dirt; public Vector3 DirtAt; public float Water; public Vector3 WaterAt; public float SunYaw = 32f, SunPitch = 40f; public Color Sun = new Color(1f, 0.94f, 0.84f);
            public bool Ortho; public float OrthoSize = 6f; public float OrbitFrom, OrbitTo, Dolly = 0.06f; public List<It> Items = new List<It>();
        }

        private static It A(string n, float x, float z, float yaw, string action = "Idle", FarmAnimalDemo.DemoMode mode = FarmAnimalDemo.DemoMode.Hold, float y = 0f, float patrol = 1.2f, float phase = -1f, bool swim = false, float scale = 1f) =>
            new It { Name = n, P = new Vector3(x, y, z), Yaw = yaw, Action = action, Mode = mode, Patrol = patrol, Phase = phase, Swim = swim, Scale = scale };
        private static It D(string n, float x, float z, float yaw = 0f, float scale = 1f, float y = 0f) =>
            new It { Name = n, P = new Vector3(x, y, z), Yaw = yaw, Scale = scale };

        private const FarmAnimalDemo.DemoMode Patrol = FarmAnimalDemo.DemoMode.Patrol;

        public static readonly Shot[] Shots =
        {
            new Shot { Name = "01_FarmMorning", Mm = 45f, Cam = new Vector3(0.6f, 1.35f, -8.4f), Look = new Vector3(0.6f, 0.85f, 0.8f), Items = {
                D("Barn", 7.0f, 9.0f, 200f), D("Fence_Rail", -0.6f, 3.9f), D("Fence_Rail", 1.5f, 3.9f), D("Fence_Rail", 3.6f, 3.9f), D("Fence_Post_End", -1.7f, 3.9f),
                D("Tree_Oak_L", -6.5f, 8.5f, 40f), D("Tree_Birch", -3.6f, 6.5f), D("Rock_M", -3.6f, -1.4f, 30f), D("Rock_S", 3.9f, -2.0f),
                D("Grass_Tuft_M", -2.4f, -2.2f), D("Grass_Tuft_M", 2.6f, -2.6f, 60f), D("Grass_Tuft_S", 4.6f, -0.8f), D("Flower_Daisy", -1.3f, -2.7f), D("Flower_Meadow", 5.0f, 1.6f),
                A("Cow", -1.7f, 1.0f, 235f, phase: 0.2f), A("Calf", -0.1f, -0.3f, 215f, "Walk", Patrol, patrol: 1.2f, phase: 0.35f), A("Sheep", 2.2f, 1.9f, 205f),
                A("Piglet", 1.6f, -0.6f, 220f, "Walk", Patrol, patrol: 0.9f), A("Rooster", 3.3f, 0.1f, 210f) } },

            new Shot { Name = "02_PastureFamilies", Mm = 55f, Cam = new Vector3(0f, 1.5f, -10.5f), Look = new Vector3(0.3f, 1.0f, 0.8f), Items = {
                D("Fence_Rail", -3.2f, 4.2f), D("Fence_Rail", -1.1f, 4.2f), D("Fence_Rail", 1.0f, 4.2f), D("Fence_Rail", 3.1f, 4.2f),
                D("Tree_Oak_L", -7f, 9f), D("Tree_Birch", 6.5f, 8f, 30f), D("Rock_M", 2.3f, -1.7f), D("Rock_S", -3.8f, -1.2f),
                D("Grass_Tuft_M", -2.6f, -2.0f), D("Grass_Tuft_S", 0.8f, -2.4f), D("Flower_Meadow", 4.6f, 0.4f),
                A("Horse", -1.7f, 0.7f, 110f, phase: 0.3f), A("Foal", -2.3f, -0.5f, 100f, "Walk", Patrol, patrol: 1.6f),
                A("Lamb", 0.9f, 0.1f, 170f), A("Goat", 2.7f, 1.6f, 205f), A("Kid", 3.5f, 1.1f, 215f, "Play_Hop") } },

            new Shot { Name = "03_ChickenYard", Mm = 42f, Cam = new Vector3(0.5f, 0.72f, -3.1f), Look = new Vector3(0.55f, 0.4f, 0.6f), Rx = 6f, Rz = 5f,
                Dirt = 3.6f, DirtAt = new Vector3(0.3f, 0f, 0.6f), Items = {
                D("Coop", -3.3f, 3.4f, 160f), D("Fence_Rail", 0.2f, 4.4f), D("Fence_Rail", 2.3f, 4.4f), D("Fence_Rail", 4.4f, 4.4f),
                D("Tree_Apple_Fruit", 4.8f, 7.5f), D("Wood_Log", -0.7f, 0.7f, 85f, 0.8f), D("Grass_Tuft_M", -3.4f, -0.8f), D("Grass_Tuft_M", 3.6f, -1.2f, 50f),
                D("Grass_Tuft_S", -2.4f, -1.6f), D("Trough_Grain", 2.9f, 2.6f, 20f),
                A("Rooster", -0.68f, 0.98f, 200f, y: 0.5f), A("Hen", 0.9f, 0.2f, 235f, "Peck"),
                A("Chick", -0.5f, -0.9f, 190f), A("Chick", 0.4f, -1.0f, 160f, "Peck"), A("Chick", 1.5f, -0.7f, 215f),
                A("Turkey", 2.4f, 1.7f, 205f, "Display") } },

            new Shot { Name = "04_DuckPond", Mm = 50f, Cam = new Vector3(0.1f, 1.6f, -4.6f), Look = new Vector3(0.1f, 0.15f, 0.6f), Water = 2.1f, WaterAt = new Vector3(-0.3f, 0f, 0.9f), Items = {
                D("Grass_Reeds", -2.9f, 2.4f, 0f, 0.6f), D("Grass_Reeds", 2.2f, 2.9f, 40f, 0.55f), D("Rock_M", -2.9f, 0.2f, 0f, 0.8f), D("Rock_S", -2.2f, -0.7f), D("Rock_M", 1.0f, 2.9f, 70f, 0.7f),
                D("Rock_Flat", 1.0f, -1.35f, 20f, 0.8f), D("Tree_Willow", -5.5f, 7.5f), D("Grass_Tuft_M", 3.4f, 1.6f), D("Water_LilyPads", 0.9f, 1.8f, 0f, 0.8f),
                A("Duck", -1.4f, 0.4f, 100f, "Swim", Patrol, patrol: 1.2f, swim: true), A("Duckling", -0.6f, 0.55f, 100f, "Swim", Patrol, patrol: 1.2f, swim: true),
                A("Duckling", -0.05f, 0.7f, 100f, "Swim", Patrol, patrol: 1.2f, swim: true), A("Duckling", 0.5f, 0.85f, 100f, "Swim", Patrol, patrol: 1.2f, swim: true),
                A("Goose", 1.65f, -0.8f, 235f), A("Frog", 1.0f, -1.35f, 200f, y: 0.13f) } },

            new Shot { Name = "05_FarmCompanions", Mm = 50f, Cam = new Vector3(0.3f, 0.95f, -5.3f), Look = new Vector3(0.4f, 0.62f, 0.6f), Items = {
                D("Shed", 1.9f, 3.3f, 180f), D("Tree_Oak_L", -6f, 7.5f), D("Bush_Round", -3.4f, 2.6f), D("RainBarrel", 3.7f, 2.2f), D("Grass_Tuft_M", -2.8f, -1.6f),
                D("Flower_Daisy", 2.9f, -1.8f), D("Grass_Tuft_S", 0.7f, -2.2f),
                A("Dog", -1.5f, 0.5f, 160f, "Sit_Idle"), A("Puppy", -0.2f, -0.8f, 200f), A("Cat", 1.4f, 1.0f, 270f, "Walk", Patrol, patrol: 1.2f), A("Kitten", 2.5f, 0.5f, 220f) } },

            new Shot { Name = "06_MeadowFriends", Mm = 65f, Cam = new Vector3(0.1f, 0.42f, -2.9f), Look = new Vector3(0.1f, 0.22f, 0.0f), Rx = 5f, Rz = 4.5f, Items = {
                D("Bush_Round", -2.6f, 2.2f), D("Bush_Flowering", 2.5f, 2.4f), D("Flower_Meadow", 0.15f, 1.0f), D("Flower_Daisy", 1.3f, 0.5f), D("Flower_Poppy", -1.9f, -0.6f),
                D("Flower_Lavender", 2.2f, -0.3f), D("Grass_Tuft_M", 0.9f, 1.6f), D("Rock_Flat", 0.25f, -1.25f, 30f, 0.45f), D("Plant_Fern", -1.4f, 1.4f),
                A("Rabbit", -0.8f, 0.6f, 150f), A("Hedgehog", 0.6f, -0.2f, 230f, "Walk", Patrol, patrol: 0.5f),
                A("Ladybug", 0.25f, -1.25f, 200f, "Walk", Patrol, y: 0.09f, patrol: 0.12f), A("Bee", -0.35f, -0.8f, 160f, "Fly", y: 0.32f), A("Butterfly", 0.75f, -0.6f, 200f, "Fly", y: 0.38f) } },

            new Shot { Name = "07_LivestockYard", Mm = 50f, Cam = new Vector3(0.4f, 1.5f, -9.2f), Look = new Vector3(0.6f, 0.95f, 0.8f), Rx = 7.5f,
                Dirt = 4.6f, DirtAt = new Vector3(0.6f, 0f, 0.8f), Items = {
                D("Stable", -4.4f, 4.4f, 160f), D("Trough_Water", 3.4f, 2.6f, 10f), D("Fence_Rail", 0.4f, 4.8f), D("Fence_Rail", 2.5f, 4.8f), D("Wagon_HayLoad", 6.0f, 5.0f, -20f),
                D("Tree_Oak_L", 8f, 10f), D("Grass_Tuft_M", -3.8f, -1.6f), D("Grass_Tuft_M", 5.2f, -1.0f),
                A("Bull", -1.9f, 0.6f, 150f), A("Donkey", 0.4f, 1.8f, 200f), A("Ram", 1.8f, 1.2f, 215f), A("Pig", 3.0f, -0.1f, 240f, "Root"), A("Piglet", 3.8f, -0.8f, 210f) } },

            new Shot { Name = "08_FarmyardBirds", Mm = 55f, Cam = new Vector3(0.1f, 0.85f, -4.0f), Look = new Vector3(0.1f, 0.72f, 0.3f), Rx = 5.5f, Rz = 4.5f, Items = {
                D("Fence_Rail", -1.0f, 0.7f), D("Shed", 2.6f, 3.4f, 180f), D("Tree_Birch", -4.8f, 5.5f), D("Rock_M", 0.75f, -0.3f, 20f, 0.9f), D("Grass_Tuft_M", -2.6f, -0.9f),
                D("Grass_Tuft_S", 0.5f, -1.4f), D("Flower_Daisy", 2.6f, 0.6f),
                A("Crow", -0.65f, 0.7f, 160f, y: 1.17f), A("Pigeon", 0.15f, -0.1f, 200f, "Peck"), A("Sparrow", 0.75f, -0.3f, 220f, y: 0.42f) } },

            new Shot { Name = "09_FoxAndMouse", Mm = 55f, Cam = new Vector3(0.35f, 0.55f, -3.8f), Look = new Vector3(0.45f, 0.28f, 0.3f), SunYaw = 70f, SunPitch = 22f,
                Sun = new Color(1f, 0.80f, 0.60f), Items = {
                D("Path_Dirt_Straight", 0.9f, 0.5f, 25f), D("Path_Dirt_Straight", 2.7f, 1.35f, 25f), D("Rock_Flat", -0.25f, -1.0f, 10f, 0.7f), D("Bush_Berry", -3.0f, 2.2f),
                D("Tree_Spruce_L", 4.6f, 7f), D("Tree_Oak_Autumn", -6f, 8f), D("Grass_Tuft_M", -2.4f, 0.4f), D("Grass_Tall", 3.8f, -0.8f),
                A("Fox", 1.3f, 0.7f, 245f, "Walk", Patrol, patrol: 1.4f), A("Mouse", -0.25f, -1.0f, 150f, y: 0.13f) } },
        };


        /// <summary>Wide video scenes: many animals, camera 35 mm, slow orbit (ShotCameraMotion). Not rendered as stills.</summary>
        public static readonly Shot[] Videos =
        {
            new Shot { Name = "V1_Farmyard", Mm = 35f, Cam = new Vector3(0f, 2.3f, -9.3f), Look = new Vector3(0f, 1.0f, 1.2f), OrbitFrom = -10f, OrbitTo = 10f, Items = {
                D("Barn", 6.5f, 9.5f, 200f), D("Fence_Rail", -5.25f, 5.2f), D("Fence_Rail", -3.15f, 5.2f), D("Fence_Rail", -1.05f, 5.2f), D("Fence_Rail", 1.05f, 5.2f), D("Fence_Rail", 3.15f, 5.2f),
                D("Tree_Oak_L", -8.5f, 11f), D("Tree_Birch", -4.5f, 9f), D("Trough_Water", 2.8f, 3.4f, 10f), D("Coop", -6.6f, 3.0f, 120f), D("Wagon_HayLoad", 8.5f, 5.5f, -20f),
                D("Rock_M", -6.0f, -1.8f), D("Grass_Tuft_M", -4.4f, -3.0f), D("Grass_Tuft_M", 4.8f, -2.6f), D("Flower_Meadow", 6.4f, -0.6f), D("Grass_Tuft_S", 1.8f, -3.2f),
                A("Bull", -5.0f, 2.6f, 160f), A("Cow", -2.5f, 1.6f, 230f), A("Calf", -1.2f, 0.2f, 210f, "Walk", Patrol, patrol: 1.6f),
                A("Sheep", 1.5f, 2.3f, 200f), A("Sheep", 2.7f, 1.4f, 215f, "Graze"), A("Lamb", 1.0f, 0.6f, 190f, "Play_Hop"),
                A("Pig", 4.4f, 0.9f, 230f, "Root"), A("Piglet", 5.1f, 0.0f, 210f, "Walk", Patrol, patrol: 1.0f), A("Piglet", 3.7f, -0.2f, 200f),
                A("Hen", -3.6f, -0.8f, 200f, "Peck"), A("Rooster", -2.6f, -1.4f, 215f), A("Chick", -3.2f, -1.9f, 190f), A("Chick", -2.1f, -2.3f, 170f, "Peck"),
                A("Dog", 0.6f, -1.6f, 270f, "Walk", Patrol, patrol: 2.2f) } },

            new Shot { Name = "V2_Pasture", Mm = 35f, Cam = new Vector3(0f, 2.4f, -10.2f), Look = new Vector3(0f, 1.1f, 1.4f), OrbitFrom = 12f, OrbitTo = -8f, Items = {
                D("Fence_Rail", -6.3f, 5.6f), D("Fence_Rail", -4.2f, 5.6f), D("Fence_Rail", -2.1f, 5.6f), D("Fence_Rail", 0f, 5.6f), D("Fence_Rail", 2.1f, 5.6f), D("Fence_Rail", 4.2f, 5.6f), D("Fence_Rail", 6.3f, 5.6f),
                D("Stable", -6.5f, 7.5f, 160f), D("Tree_Oak_L", 7.5f, 10.5f), D("Tree_Birch", -10f, 8f), D("Tree_Apple_Fruit", 3f, 10f), D("Rock_M", 4.6f, -2.0f),
                D("Flower_Meadow", -5.5f, -1.5f), D("Grass_Tuft_M", -2.6f, -2.8f), D("Grass_Tuft_M", 2.4f, -3.0f), D("Bush_Round", 8.5f, 3.5f),
                A("Horse", -3.0f, 1.6f, 100f, "Walk", Patrol, patrol: 2.6f), A("Foal", -3.6f, 0.3f, 95f, "Walk", Patrol, patrol: 2.2f), A("Donkey", -0.5f, 2.7f, 200f, "Graze"),
                A("Goat", 2.6f, 1.9f, 210f, "Browse"), A("Kid", 3.4f, 1.0f, 215f, "Play_Hop"), A("Ram", 5.1f, 2.8f, 200f),
                A("Sheep", 1.0f, 0.5f, 190f, "Graze"), A("Lamb", 0.4f, -0.7f, 180f), A("Lamb", 2.0f, -0.5f, 200f, "Play_Hop"),
                A("Dog", -1.3f, -1.7f, 150f, "Sit_Idle"), A("Puppy", -0.2f, -2.2f, 90f, "Walk", Patrol, patrol: 1.6f) } },

            new Shot { Name = "V3_PondAndBirds", Mm = 35f, Cam = new Vector3(0.4f, 2.5f, -8.0f), Look = new Vector3(0.4f, 0.6f, 1.0f), OrbitFrom = -10f, OrbitTo = 10f,
                Water = 2.6f, WaterAt = new Vector3(-2.6f, 0f, 1.6f), Items = {
                D("Grass_Reeds", -5.6f, 3.4f, 0f, 0.6f), D("Grass_Reeds", -0.6f, 4.0f, 40f, 0.55f), D("Rock_M", -5.8f, 0.6f, 0f, 0.8f), D("Rock_Flat", -0.6f, -1.2f, 20f, 0.8f),
                D("Water_LilyPads", -2.0f, 2.4f, 0f, 0.8f), D("Tree_Willow", -8f, 7f), D("Coop", 6.0f, 3.8f, 200f), D("Fence_Rail", 3.3f, 2.3f), D("Rock_M", -3.6f, -1.6f, 40f, 0.6f),
                D("Tree_Apple_Fruit", 7.5f, 8.5f), D("Grass_Tuft_M", 1.6f, -3.0f), D("Grass_Tuft_M", 6.5f, -1.5f),
                A("Duck", -4.2f, 1.2f, 100f, "Swim", Patrol, patrol: 2.0f, swim: true), A("Duckling", -3.4f, 1.35f, 100f, "Swim", Patrol, patrol: 2.0f, swim: true),
                A("Duckling", -2.8f, 1.5f, 100f, "Swim", Patrol, patrol: 2.0f, swim: true), A("Duckling", -2.2f, 1.65f, 100f, "Swim", Patrol, patrol: 2.0f, swim: true),
                A("Goose", 0.4f, 0.3f, 230f, "Graze"), A("Frog", -0.6f, -1.2f, 200f, y: 0.13f),
                A("Hen", 3.0f, 0.4f, 220f, "Peck"), A("Hen", 4.3f, -0.5f, 200f, "Peck"), A("Rooster", 2.3f, -0.7f, 200f), A("Turkey", 5.1f, 1.3f, 205f, "Display"),
                A("Chick", 3.5f, -1.3f, 190f), A("Chick", 4.1f, -1.7f, 170f, "Peck"), A("Chick", 2.9f, -1.9f, 210f),
                A("Pigeon", 1.4f, -1.9f, 200f, "Peck"), A("Pigeon", 0.8f, -2.4f, 230f), A("Crow", 3.3f, 2.3f, 170f, y: 1.17f), A("Sparrow", -3.6f, -1.6f, 200f, y: 0.4f) } },

            new Shot { Name = "V4_Garden", Mm = 35f, Cam = new Vector3(0.3f, 1.5f, -5.9f), Look = new Vector3(0.3f, 0.55f, 0.6f), OrbitFrom = 10f, OrbitTo = -10f, Items = {
                D("Shed", 3.2f, 4.4f, 190f), D("Tree_Apple_Blossom", -5f, 6f), D("Bush_Flowering", -2.8f, 3.4f), D("Bush_Round", 0.4f, 4.0f), D("Hedge_Straight", 6.2f, 2.6f, 90f),
                D("Flower_Daisy", -1.2f, -1.0f), D("Flower_Tulip", 1.6f, 0.6f), D("Flower_Lavender", -3.4f, 0.8f), D("Flower_Poppy", 2.6f, -1.6f), D("Flower_Meadow", -0.4f, 1.6f),
                D("Rock_Flat", 0.2f, -1.9f, 30f, 0.6f), D("Rock_Flat", -1.9f, -1.7f, 70f, 0.5f), D("Path_Stepping_Stones", 1.2f, 2.0f, 20f), D("Grass_Tuft_M", 4.0f, -1.0f),
                A("Cat", -1.6f, 0.8f, 270f, "Walk", Patrol, patrol: 1.6f), A("Kitten", -0.5f, 0.1f, 200f, "Pounce"), A("Puppy", 1.0f, -0.3f, 200f, "Play_Bow"),
                A("Rabbit", -2.7f, -0.6f, 150f, "Nibble"), A("Hedgehog", 2.3f, -1.1f, 230f, "Walk", Patrol, patrol: 0.7f), A("Fox", 4.2f, 0.6f, 250f, "Walk", Patrol, patrol: 2.0f),
                A("Mouse", 0.2f, -1.9f, 160f, y: 0.12f), A("Ladybug", -1.9f, -1.7f, 200f, "Walk", Patrol, y: 0.1f, patrol: 0.12f),
                A("Bee", -1.1f, -1.0f, 160f, "Fly", y: 0.6f), A("Bee", 1.7f, 0.5f, 200f, "Fly", y: 0.7f), A("Butterfly", -0.3f, 1.5f, 190f, "Fly", y: 0.8f), A("Butterfly", 2.7f, -1.5f, 220f, "Fly", y: 0.75f) } },
        };

        // ---------------- build ----------------
        [MenuItem("Tools/Farm Animals/Presentation/Build Shot Scenes")]
        public static string BuildAll()
        {
            Directory.CreateDirectory(SceneDir); Directory.CreateDirectory(MeshDir);
            FarmAnimalsDemoBuilder.Materials();
            var log = new List<string>();
            foreach (var s in Shots.Concat(new[] { AllAnimals() }).Concat(Videos)) log.Add(Build(s));
            AssetDatabase.SaveAssets();
            return string.Join("\n", log);
        }

        private static readonly Dictionary<string, string> PrefabPaths = new Dictionary<string, string>();
        private static GameObject Prefab(string name)
        {
            if (PrefabPaths.Count == 0)
                foreach (var g in AssetDatabase.FindAssets("t:Prefab", new[] { "Assets/FarmAnimals/Art/Prefabs", "Assets/_Presentation" }))
                {
                    var p = AssetDatabase.GUIDToAssetPath(g);
                    PrefabPaths[Path.GetFileNameWithoutExtension(p)] = p;
                }
            if (!PrefabPaths.TryGetValue("FMS_" + name, out var path)) throw new System.Exception("no prefab FMS_" + name);
            return AssetDatabase.LoadAssetAtPath<GameObject>(path);
        }

        private static bool IsAnimal(string name) => AssetDatabase.FindAssets($"FMS_{name} t:Prefab", new[] { "Assets/FarmAnimals/Art/Prefabs" })
            .Any(g => Path.GetFileNameWithoutExtension(AssetDatabase.GUIDToAssetPath(g)) == "FMS_" + name);

        private static string Build(Shot s)
        {
            var scene = FarmAnimalsDemoBuilder.NewScene(out var world, "Assets/_Presentation/Settings/PP_Presentation.asset");
            var sun = Object.FindObjectsByType<Light>(FindObjectsSortMode.None).First();   // allow-rule: editor scene builder, the light it just created
            sun.transform.rotation = Quaternion.Euler(s.SunPitch, s.SunYaw, 0f);
            sun.color = s.Sun;
            // the island holds EVERY object of the shot (trees and buildings far behind too) with a margin, flat top
            var rx = Mathf.Max(s.Rx, s.Items.Max(i => Mathf.Abs(i.P.x)) + 3f);
            var rz = Mathf.Max(s.Rz, s.Items.Max(i => Mathf.Abs(i.P.z)) + 3f);
            var k = s.Items.Max(i => Mathf.Sqrt(Mathf.Pow(i.P.x / rx, 2f) + Mathf.Pow(i.P.z / rz, 2f))) / 0.8f;   // elliptic top: corners too
            if (k > 1f) { rx *= k; rz *= k; }
            var island = FarmAnimalsDemoBuilder.Island(s.Name, world, rx, rz, out _, 0f);
            if (s.Dirt > 0f)
            {
                var dirt = new GameObject("DirtYard");
                dirt.transform.SetParent(island, false);
                dirt.transform.localPosition = s.DirtAt + Vector3.up * 0.006f;
                dirt.AddComponent<MeshFilter>().sharedMesh = PatchMesh(s.Name, s.Dirt);
                dirt.AddComponent<MeshRenderer>().sharedMaterial = FarmAnimalsDemoBuilder.Lit("M_Demo_Dirt", new Color(0.70f, 0.52f, 0.33f));
            }
            if (s.Water > 0f)
            {
                var water = new GameObject("Water");
                water.transform.SetParent(island, false);
                water.transform.localPosition = s.WaterAt + Vector3.up * 0.012f;
                water.AddComponent<MeshFilter>().sharedMesh = PatchMesh("Water_" + s.Name, s.Water);
                var wm = FarmAnimalsDemoBuilder.Lit("M_Demo_Water", new Color(0.33f, 0.62f, 0.86f));
                wm.SetFloat("_Smoothness", 0.75f);
                water.AddComponent<MeshRenderer>().sharedMaterial = wm;
            }
            var decor = new GameObject("Decor").transform; decor.SetParent(island, false);
            var animals = new GameObject("Animals").transform; animals.SetParent(island, false);
            Physics.SyncTransforms();
            var count = 0;
            foreach (var it in s.Items.Where(i => !IsAnimal(i.Name)))
                Instance(it, decor);
            var decorLog = GroundDecor(decor, island);
            Physics.SyncTransforms();
            foreach (var it in s.Items.Where(i => IsAnimal(i.Name)))
            {
                var go = Instance(it, animals);
                if (it.Swim) go.transform.position = new Vector3(go.transform.position.x, (s.Water > 0f ? 0.012f : WaterY(go.transform.position)) - FarmAnimalsDemoBuilder.Animal(it.Name).Bounds.size.y * 0.22f, go.transform.position.z);
                var info = FarmAnimalsDemoBuilder.Animal(it.Name);
                var demo = go.AddComponent<FarmAnimalDemo>();
                demo.Configure(it.Mode, info.Extras, info.Locomotion, info.Walk, info.Fast, 1.2f, info.Forward);
                demo.ConfigureAction(it.Action, it.Patrol, it.Swim ? 0.22f : Mathf.Max(0.05f, info.Walk * 0.5f));
                go.name = $"{go.name}|{it.Action}|{it.Phase:F2}";                 // read back by the renderer
                count++;
            }

            var cam = new GameObject("Main Camera") { tag = "MainCamera" }.AddComponent<Camera>();
            cam.transform.position = s.Cam;
            cam.transform.LookAt(s.Look);
            cam.fieldOfView = 2f * Mathf.Atan(12f / s.Mm) * Mathf.Rad2Deg;     // full-frame 24 mm sensor height
            cam.orthographic = s.Ortho; cam.orthographicSize = s.OrthoSize;
            cam.nearClipPlane = 0.05f; cam.farClipPlane = 300f;
            FarmAnimalsDemoBuilder.Post(cam);
            var d = Vector3.Distance(s.Cam, s.Look);
            RenderSettings.fogStartDistance = d * 2.2f; RenderSettings.fogEndDistance = d * 6f;
            if (s.OrbitFrom != 0f || s.OrbitTo != 0f)
            {
                var motion = cam.gameObject.AddComponent<ShotCameraMotion>();
                motion.Target = s.Look; motion.YawFrom = s.OrbitFrom; motion.YawTo = s.OrbitTo; motion.Dolly = s.Dolly; motion.Seconds = 10f;
            }
            var rec = cam.gameObject.AddComponent<ShotRecorder>();
            rec.enabled = false;

            var ground = GroundAnimals(true);
            var path = $"{SceneDir}/Shot_{s.Name}.unity";
            EditorSceneManager.SaveScene(scene, path);
            return $"{s.Name}: {count} animals, {s.Items.Count - count} props -> {path}\n{decorLog}\n{ground}";
        }

        private static GameObject Instance(It it, Transform parent)
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(Prefab(it.Name), parent);
            go.transform.localPosition = it.P;
            go.transform.localRotation = Quaternion.Euler(0f, it.Yaw, 0f);
            go.transform.localScale = Vector3.one * it.Scale;
            return go;
        }

        private static float WaterY(Vector3 p)
        {
            foreach (var mf in Object.FindObjectsByType<MeshFilter>(FindObjectsSortMode.None).Where(m => m.name.Contains("Pond")))   // allow-rule: editor scene builder
                if (mf.GetComponent<MeshCollider>() == null) mf.gameObject.AddComponent<MeshCollider>();
            Physics.SyncTransforms();
            // the pond is one mesh (rim rocks, reeds, water): the water is the lowest surface hit around this point
            var ys = new List<float>();
            for (var i = -2; i <= 2; i++) for (var j = -2; j <= 2; j++)
                foreach (var h in Physics.RaycastAll(p + new Vector3(i * 0.15f, 5f, j * 0.15f), Vector3.down, 10f))
                    if (h.collider.name.Contains("Pond")) ys.Add(h.point.y);
            return ys.Count > 0 ? ys.Min() : 0f;
        }

        private static Shot AllAnimals()
        {
            string[][] rows =
            {
                new[] { "Bull", "Cow", "Horse", "Donkey", "Ram", "Sheep", "Goat" },
                new[] { "Calf", "Foal", "Pig", "Lamb", "Kid", "Piglet", "Dog" },
                new[] { "Turkey", "Goose", "Fox", "Puppy", "Cat", "Rabbit", "Hen" },
                new[] { "Rooster", "Duck", "Crow", "Pigeon", "Kitten", "Hedgehog", "Sparrow" },
                new[] { "Chick", "Duckling", "Frog", "Mouse", "Bee", "Butterfly", "Ladybug" },
            };
            var shot = new Shot { Name = "10_AllAnimals", Ortho = true, Rx = 11f, Rz = 7.5f };
            var depth = new[] { 2.6f, 2.0f, 1.5f, 1.2f, 1.0f };
            var z = 4.4f;
            for (var r = 0; r < rows.Length; r++)
            {
                var widths = rows[r].Select(n => Mathf.Max(0.7f, FarmAnimalsDemoBuilder.Animal(n).Bounds.size.x * 1.2f + 0.9f)).ToArray();
                var x = -widths.Sum() / 2f;
                for (var i = 0; i < rows[r].Length; i++)
                {
                    var n = rows[r][i]; var info = FarmAnimalsDemoBuilder.Animal(n);
                    var s = Mathf.Clamp(0.45f / Mathf.Max(0.01f, info.Bounds.size.y), 1f, 4f);   // the smallest ones scaled up to read
                    var y = FarmAnimalsDemoBuilder.Fliers.Contains(n) ? 0.25f : 0f;
                    shot.Items.Add(A(n, x + widths[i] / 2f, z, 205f, FarmAnimalsDemoBuilder.Fliers.Contains(n) ? "Fly" : "Idle", FarmAnimalDemo.DemoMode.Cycle, y: y, scale: s));
                    x += widths[i];
                }
                z -= depth[r];
            }
            shot.Cam = new Vector3(0f, 13.5f, -25f); shot.Look = new Vector3(0f, 0.5f, 0.3f); shot.OrthoSize = 4.6f; shot.Rx = 10.5f; shot.Rz = 7f; shot.OrbitFrom = -14f; shot.OrbitTo = 14f; shot.Dolly = 0f;
            return shot;
        }

        private static Mesh PatchMesh(string name, float r)
        {
            var path = $"{MeshDir}/Dirt_{name}.asset";
            var mesh = AssetDatabase.LoadAssetAtPath<Mesh>(path);
            if (mesh == null) { mesh = new Mesh(); AssetDatabase.CreateAsset(mesh, path); }
            var rnd = new System.Random(name.GetHashCode());
            const int n = 16;
            var v = new List<Vector3> { Vector3.zero }; var t = new List<int>();
            for (var k = 0; k < n; k++)
            {
                var a = k / (float)n * Mathf.PI * 2f; var rr = r * (0.85f + (float)rnd.NextDouble() * 0.25f);
                v.Add(new Vector3(Mathf.Cos(a) * rr * 1.25f, 0f, Mathf.Sin(a) * rr));
            }
            for (var k = 0; k < n; k++) { t.Add(0); t.Add(1 + (k + 1) % n); t.Add(1 + k); }
            mesh.Clear(); mesh.SetVertices(v); mesh.SetTriangles(t, 0); mesh.RecalculateNormals(); mesh.RecalculateBounds();
            EditorUtility.SetDirty(mesh);
            return mesh;
        }

        // ---------------- grounding ----------------
        /// <summary>
        /// For every animal of the open scene (swimmers and flying insects skipped): samples its shot clip at 12 phases,
        /// takes the lowest vertex over the cycle and ray-casts the surface under it (island, log, fence, rock; temporary
        /// MeshColliders on all non-animal meshes). apply = move the animal so that lowest vertex sits 2 mm into the surface.
        /// Returns one line per animal with the gap before the fix (+ = floating, - = sunk), in cm.
        /// </summary>
        public static string GroundAnimals(bool apply)
        {
            var scene = EditorSceneManager.GetActiveScene();
            var animators = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Animator>()).ToList();
            var temp = new List<Collider>();
            // the surface is measured on the real geometry: a temporary MeshCollider on every non-animal mesh; the props'
            // own simplified colliders (boxes around fences and rocks) are switched off, they sit above the visible top
            var off = new List<Collider>();
            foreach (var c in scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Collider>()))
                if (c.enabled) { c.enabled = false; off.Add(c); }
            foreach (var mf in scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<MeshFilter>()))
                if (mf.GetComponentInParent<Animator>() == null && !mf.name.StartsWith("Cloud") && !mf.name.ToUpperInvariant().Contains("_LOD") && mf.sharedMesh != null && mf.GetComponent<MeshRenderer>() != null && mf.GetComponent<MeshRenderer>().enabled)
                    temp.Add(mf.gameObject.AddComponent<MeshCollider>());
            var lines = new List<string>();
            try
            {
                foreach (var a in animators)
                {
                    var parts = a.name.Split('|');
                    var species = parts[0].Substring(4); var dash = species.IndexOf('_'); if (dash > 0 && char.IsDigit(species[species.Length - 1])) species = species.Substring(0, dash);
                    var action = parts.Length > 1 ? parts[1] : "Idle";
                    if (action == "Swim" || FarmAnimalsDemoBuilder.Fliers.Contains(species)) continue;
                    var clip = ClipFor(a, species, action);
                    var min = float.MaxValue; var at = Vector3.zero; var baked = new Mesh();
                    AnimationMode.StartAnimationMode();
                    try
                    {
                        for (var k = 0; k < 12; k++)
                        {
                            AnimationMode.BeginSampling();
                            AnimationMode.SampleAnimationClip(a.gameObject, clip, k / 12f * clip.length);
                            AnimationMode.EndSampling();
                            foreach (var r in a.GetComponentsInChildren<SkinnedMeshRenderer>())
                            {
                                r.BakeMesh(baked, true);
                                foreach (var v in baked.vertices)
                                {
                                    var w = r.transform.TransformPoint(v);
                                    if (w.y < min) { min = w.y; at = w; }
                                }
                            }
                        }
                    }
                    finally { AnimationMode.StopAnimationMode(); Object.DestroyImmediate(baked); }
                    var own = a.GetComponentsInChildren<Collider>(); foreach (var c in own) c.enabled = false;
                    Physics.SyncTransforms();
                    var hit = Physics.Raycast(new Vector3(at.x, min + 0.6f, at.z), Vector3.down, out var h, 3f);
                    foreach (var c in own) c.enabled = true;
                    var groundY = hit ? h.point.y : 0f;
                    var gap = min - groundY;
                    if (apply && Mathf.Abs(gap + 0.002f) > 0.001f) a.transform.position -= Vector3.up * (gap + 0.002f);
                    lines.Add($"   {a.name.Split('|')[0],-16} {action,-10} gap {gap * 100f,6:F1} cm on {(hit ? h.collider.name : "nothing")}{(Mathf.Abs(gap) > 0.01f ? (apply ? "  fixed" : "  !") : "")}");
                }
            }
            finally { foreach (var c in temp) Object.DestroyImmediate(c); foreach (var c in off) c.enabled = true; }
            return string.Join("\n", lines);
        }

        /// <summary>Every prop stands on the island: its lowest vertex is moved to the island surface under it (ray on
        /// the island mesh only), so nothing floats at the edge or sinks. Returns the props that were off by > 1 cm.</summary>
        private static string GroundDecor(Transform decor, Transform island)
        {
            var groundGo = island.Find("IslandGround").gameObject;
            var mc = groundGo.AddComponent<MeshCollider>();
            var lines = new List<string>();
            try
            {
                Physics.SyncTransforms();
                foreach (Transform t in decor)
                {
                    var rs = t.GetComponentsInChildren<Renderer>();
                    if (rs.Length == 0) continue;
                    var min = float.MaxValue; var at = Vector3.zero;
                    foreach (var r in rs)
                    {
                        if (!(r is MeshRenderer) || !r.TryGetComponent<MeshFilter>(out var mf) || mf.sharedMesh == null) continue;
                        foreach (var v in mf.sharedMesh.vertices)
                        {
                            var w = r.transform.TransformPoint(v);
                            if (w.y < min) { min = w.y; at = w; }
                        }
                    }
                    var c = t.position;
                    var ok = mc.Raycast(new Ray(new Vector3(c.x, 20f, c.z), Vector3.down), out var hit, 40f);
                    if (!ok) { lines.Add($"   {t.name,-26} OFF THE ISLAND"); continue; }
                    var gap = min - hit.point.y;
                    if (Mathf.Abs(gap) > 0.002f) t.position -= Vector3.up * gap;
                    if (Mathf.Abs(gap) > 0.01f) lines.Add($"   {t.name,-26} prop gap {gap * 100f:F1} cm fixed");
                }
            }
            finally { Object.DestroyImmediate(mc); }
            return lines.Count > 0 ? string.Join("\n", lines) : "   props: all on the ground";
        }

        private static AnimationClip ClipFor(Animator a, string species, string action)
        {
            var clips = a.runtimeAnimatorController.animationClips;
            var key = action == "Walk" ? new[] { "Walk", "Hop", "Scurry", "Crawl" } : action == "Fast" ? new[] { "Run", "Trot" } : new[] { action };
            return key.Select(k => clips.FirstOrDefault(c => c.name == $"{species}_{k}")).FirstOrDefault(c => c != null)
                   ?? clips.FirstOrDefault(c => c.name == $"{species}_Idle") ?? clips[0];
        }

        // ---------------- renders ----------------
        [MenuItem("Tools/Farm Animals/Presentation/Render All Shots")]
        public static string RenderAll()
        {
            var outs = new List<string>();
            foreach (var path in Directory.GetFiles(SceneDir, "Shot_*.unity").Where(p => !Path.GetFileName(p).StartsWith("Shot_V")).OrderBy(p => p))
            {
                EditorSceneManager.OpenScene(path.Replace('\\', '/'));
                outs.Add(RenderOpen($"{MediaDir}/{Path.GetFileNameWithoutExtension(path).Substring(5)}.png"));
            }
            return string.Join("\n", outs);
        }

        public static string RenderOpen(string outPath, int width = 1920, int height = 1080, int supersample = 2)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(outPath));
            var scene = EditorSceneManager.GetActiveScene();
            var cam = scene.GetRootGameObjects().Select(g => g.GetComponent<Camera>()).First(c => c != null && c.name == "Main Camera");
            var urp = (UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            var oldDist = urp.shadowDistance; var oldRes = urp.mainLightShadowmapResolution;
            urp.shadowDistance = 60f; urp.mainLightShadowmapResolution = 4096;
            var rnd = new System.Random(scene.name.GetHashCode());
            AnimationMode.StartAnimationMode();
            try
            {
                AnimationMode.BeginSampling();
                foreach (var a in scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Animator>()))
                {
                    var parts = a.name.Split('|');
                    var species = parts[0].Substring(4);
                    var action = parts.Length > 1 ? parts[1] : "Idle";
                    var phase = parts.Length > 2 && float.TryParse(parts[2], System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out var ph) && ph >= 0f ? ph : (float)rnd.NextDouble();
                    var clips = a.runtimeAnimatorController.animationClips;
                    var key = action == "Walk" ? new[] { "Walk", "Hop", "Scurry", "Crawl" } : action == "Fast" ? new[] { "Run", "Trot" } : new[] { action };
                    var clip = key.Select(k => clips.FirstOrDefault(c => c.name == $"{species}_{k}")).FirstOrDefault(c => c != null)
                               ?? clips.FirstOrDefault(c => c.name == $"{species}_Idle") ?? clips[0];
                    AnimationMode.SampleAnimationClip(a.gameObject, clip, phase * clip.length);
                }
                AnimationMode.EndSampling();
                var rt = new RenderTexture(width * supersample, height * supersample, 24) { antiAliasing = 8 };
                cam.targetTexture = rt; cam.aspect = width / (float)height;
                cam.Render();
                cam.targetTexture = null;
                var final = new RenderTexture(width, height, 0);
                Graphics.Blit(rt, final);
                RenderTexture.active = final;
                var tex = new Texture2D(width, height, TextureFormat.RGB24, false);
                tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
                RenderTexture.active = null;
                File.WriteAllBytes(outPath, tex.EncodeToPNG());
                Object.DestroyImmediate(tex); Object.DestroyImmediate(rt); Object.DestroyImmediate(final);
            }
            finally
            {
                AnimationMode.StopAnimationMode();
                urp.shadowDistance = oldDist; urp.mainLightShadowmapResolution = oldRes;
            }
            return outPath;
        }

        // ---------------- video ----------------
        /// <summary>Opens a shot scene, enables its ShotRecorder and enters Play mode; frames go to %TEMP%/FarmAnimals_video/&lt;shot&gt;.</summary>
        public static string Record(string shot, float seconds = 8f)
        {
            EditorSceneManager.OpenScene($"{SceneDir}/Shot_{shot}.unity");
            var rec = Object.FindObjectsByType<ShotRecorder>(FindObjectsInactive.Include, FindObjectsSortMode.None).First();   // allow-rule: editor recording helper
            var dir = Path.Combine(Path.GetTempPath(), "FarmAnimals_video", shot);
            if (Directory.Exists(dir)) Directory.Delete(dir, true);
            rec.OutputDir = dir; rec.Seconds = seconds; rec.enabled = true;
            EditorApplication.isPlaying = true;
            return dir;
        }
    }
}
