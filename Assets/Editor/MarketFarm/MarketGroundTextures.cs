using System.IO;
using UnityEditor;
using UnityEngine;

namespace MarketFarm.Editor
{
    /// <summary>
    /// Procedural, seamlessly tiling ground textures (cobblestone and lush grass) with normal maps.
    /// Generated once into Art/MarketFarm/Materials; delete the PNGs to regenerate.
    /// </summary>
    internal static class MarketGroundTextures
    {
        private const int Size = 512;
        private const string Dir = MarketSceneBuilder.MaterialDir;

        internal static Material Cobble(string materialName, Vector2 tiling) => Cobble(Dir, materialName, tiling);

        internal static Material Grass(string materialName, Vector2 tiling) => Grass(Dir, materialName, tiling);

        internal static Material Cobble(string dir, string materialName, Vector2 tiling)
        {
            EnsureTextures(dir, "T_Ground_Cobble", GenerateCobble);
            return MakeMaterial(dir, materialName, "T_Ground_Cobble", tiling, 0.18f, 1.0f);
        }

        internal static Material Grass(string dir, string materialName, Vector2 tiling)
        {
            EnsureTextures(dir, "T_Ground_Grass", GenerateGrass);
            return MakeMaterial(dir, materialName, "T_Ground_Grass", tiling, 0.04f, 0.6f);
        }

        internal static Material Dirt(string dir, string materialName, Vector2 tiling)
        {
            EnsureTextures(dir, "T_Ground_Dirt", GenerateDirt);
            return MakeMaterial(dir, materialName, "T_Ground_Dirt", tiling, 0.06f, 0.8f);
        }

        // ---------- Generators: fill base colour and height, normal is derived from height ----------

        private static void GenerateCobble(Color[] colour, float[] height)
        {
            const int cells = 7;
            var palette = new[]
            {
                new Color(0.86f, 0.78f, 0.64f), new Color(0.80f, 0.74f, 0.66f), new Color(0.90f, 0.80f, 0.62f),
                new Color(0.76f, 0.72f, 0.68f), new Color(0.84f, 0.71f, 0.58f),
            };
            var mortar = new Color(0.40f, 0.36f, 0.31f);
            for (var y = 0; y < Size; y++)
            for (var x = 0; x < Size; x++)
            {
                var p = new Vector2((float)x / Size * cells, (float)y / Size * cells);
                float f1 = 9f, f2 = 9f; int id1 = 0;
                var cx = Mathf.FloorToInt(p.x); var cy = Mathf.FloorToInt(p.y);
                for (var j = -1; j <= 1; j++)
                for (var i = -1; i <= 1; i++)
                {
                    var gx = cx + i; var gy = cy + j;
                    var wx = ((gx % cells) + cells) % cells; var wy = ((gy % cells) + cells) % cells;
                    var h = Hash(wx, wy);
                    var fp = new Vector2(gx + 0.15f + 0.7f * Frac(h * 7.13f), gy + 0.15f + 0.7f * Frac(h * 3.71f));
                    var d = Vector2.Distance(p, fp);
                    if (d < f1) { f2 = f1; f1 = d; id1 = wx * 131 + wy; }
                    else if (d < f2) f2 = d;
                }
                var edge = f2 - f1;
                var stoneMask = Smoothstep(0.015f, 0.09f, edge);
                var hh = Hash(id1, 7);
                var stone = Color.Lerp(palette[(int)(Frac(hh * 5.3f) * palette.Length) % palette.Length], Color.white, 0.0f);
                var shade = 0.92f + 0.16f * Frac(hh * 11.7f);
                var grain = 0.92f + 0.16f * Noise(x * 0.35f, y * 0.35f, Size * 0.35f, 3f);
                var c = stone * (shade * grain);
                c.a = 1f;
                colour[y * Size + x] = Color.Lerp(mortar, c, stoneMask);
                // Domed stones: raised in the middle, mortar sunk.
                height[y * Size + x] = stoneMask * (0.55f + 0.45f * Mathf.Clamp01(1f - f1 * 0.9f)) + 0.04f * grain;
            }
        }

        private static void GenerateGrass(Color[] colour, float[] height)
        {
            var dark = new Color(0.24f, 0.50f, 0.12f);
            var mid = new Color(0.34f, 0.62f, 0.15f);
            var light = new Color(0.46f, 0.72f, 0.20f);
            var rng = new System.Random(3);
            for (var y = 0; y < Size; y++)
            for (var x = 0; x < Size; x++)
            {
                var low = Noise(x, y, Size, 9f) * 0.45f + Noise(x, y, Size, 23f) * 0.55f;
                var c = low < 0.5f ? Color.Lerp(dark, mid, low * 2f) : Color.Lerp(mid, light, (low - 0.5f) * 2f);
                var fine = 0.9f + 0.2f * Noise(x, y, Size, 64f);
                colour[y * Size + x] = new Color(c.r * fine, c.g * fine, c.b * fine, 1f);
                height[y * Size + x] = 0.5f + 0.25f * Noise(x, y, Size, 48f);
            }
            // Blades: short bright and dark strokes, wrapped around the edges.
            for (var n = 0; n < 9000; n++)
            {
                var bx = rng.Next(Size); var by = rng.Next(Size);
                var len = 3 + rng.Next(6);
                var lean = (float)(rng.NextDouble() - 0.5) * 0.6f;
                var tint = rng.NextDouble() < 0.5 ? new Color(0.62f, 0.86f, 0.28f) : new Color(0.14f, 0.38f, 0.08f);
                for (var k = 0; k < len; k++)
                {
                    var px = ((bx + Mathf.RoundToInt(lean * k)) % Size + Size) % Size;
                    var py = (by + k) % Size;
                    var t = 1f - (float)k / len;
                    colour[py * Size + px] = Color.Lerp(colour[py * Size + px], tint, 0.55f * t + 0.15f);
                    height[py * Size + px] += 0.15f * t;
                }
            }
        }

        private static void GenerateDirt(Color[] colour, float[] height)
        {
            var dark = new Color(0.50f, 0.37f, 0.25f);
            var mid = new Color(0.64f, 0.49f, 0.33f);
            var light = new Color(0.76f, 0.62f, 0.44f);
            var pebble = new Color(0.80f, 0.74f, 0.64f);
            var rng = new System.Random(17);
            for (var y = 0; y < Size; y++)
            for (var x = 0; x < Size; x++)
            {
                var low = Noise(x, y, Size, 6f) * 0.5f + Noise(x, y, Size, 19f) * 0.5f;
                var c = low < 0.5f ? Color.Lerp(dark, mid, low * 2f) : Color.Lerp(mid, light, (low - 0.5f) * 2f);
                var fine = 0.92f + 0.16f * Noise(x, y, Size, 80f);
                colour[y * Size + x] = new Color(c.r * fine, c.g * fine, c.b * fine, 1f);
                height[y * Size + x] = 0.4f * low + 0.1f * fine;
            }
            // Pebbles: small light dots, raised.
            for (var n = 0; n < 900; n++)
            {
                var cx = rng.Next(Size); var cy = rng.Next(Size);
                var r = 1.5f + (float)rng.NextDouble() * 3f;
                var tint = Color.Lerp(pebble, mid, (float)rng.NextDouble() * 0.5f);
                for (var dy = -5; dy <= 5; dy++)
                for (var dx = -5; dx <= 5; dx++)
                {
                    var d = Mathf.Sqrt(dx * dx + dy * dy) / r;
                    if (d > 1f) continue;
                    var px = ((cx + dx) % Size + Size) % Size; var py = ((cy + dy) % Size + Size) % Size;
                    colour[py * Size + px] = Color.Lerp(colour[py * Size + px], tint, Smoothstep(1f, 0.6f, d));
                    height[py * Size + px] += 0.35f * (1f - d * d);
                }
            }
        }

        // ---------- Plumbing ----------

        private static void EnsureTextures(string dir, string name, System.Action<Color[], float[]> generate)
        {
            Directory.CreateDirectory(dir);
            var basePath = $"{dir}/{name}_BaseColor.png";
            var normalPath = $"{dir}/{name}_Normal.png";
            if (File.Exists(basePath) && File.Exists(normalPath)) return;

            var colour = new Color[Size * Size];
            var height = new float[Size * Size];
            generate(colour, height);

            WritePng(basePath, colour);
            WritePng(normalPath, NormalFromHeight(height, 1.4f));
            Configure(basePath, false);
            Configure(normalPath, true);
        }

        private static Color[] NormalFromHeight(float[] h, float strength)
        {
            var result = new Color[Size * Size];
            for (var y = 0; y < Size; y++)
            for (var x = 0; x < Size; x++)
            {
                float H(int px, int py) => h[((py % Size + Size) % Size) * Size + ((px % Size + Size) % Size)];
                var dx = (H(x + 1, y) - H(x - 1, y)) * strength;
                var dy = (H(x, y + 1) - H(x, y - 1)) * strength;
                var n = new Vector3(-dx, -dy, 1f).normalized;
                result[y * Size + x] = new Color(n.x * 0.5f + 0.5f, n.y * 0.5f + 0.5f, n.z * 0.5f + 0.5f, 1f);
            }
            return result;
        }

        private static void WritePng(string path, Color[] pixels)
        {
            var tex = new Texture2D(Size, Size, TextureFormat.RGBA32, false);
            tex.SetPixels(pixels);
            File.WriteAllBytes(path, tex.EncodeToPNG());
            Object.DestroyImmediate(tex);
            AssetDatabase.ImportAsset(path);
        }

        private static void Configure(string path, bool normalMap)
        {
            var importer = (TextureImporter)AssetImporter.GetAtPath(path);
            importer.textureType = normalMap ? TextureImporterType.NormalMap : TextureImporterType.Default;
            importer.sRGBTexture = !normalMap;
            importer.wrapMode = TextureWrapMode.Repeat;
            importer.filterMode = FilterMode.Trilinear;
            importer.anisoLevel = 8;
            importer.mipmapEnabled = true;
            importer.SaveAndReimport();
        }

        private static Material MakeMaterial(string dir, string materialName, string textureName, Vector2 tiling, float smoothness, float bumpScale)
        {
            var path = $"{dir}/{materialName}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>($"{dir}/{textureName}_BaseColor.png"));
            mat.SetTexture("_BumpMap", AssetDatabase.LoadAssetAtPath<Texture2D>($"{dir}/{textureName}_Normal.png"));
            mat.EnableKeyword("_NORMALMAP");
            mat.SetFloat("_BumpScale", bumpScale);
            mat.SetColor("_BaseColor", Color.white);
            mat.SetFloat("_Metallic", 0f);
            mat.SetFloat("_Smoothness", smoothness);
            mat.SetTextureScale("_BaseMap", tiling);
            mat.SetTextureScale("_BumpMap", tiling);
            EditorUtility.SetDirty(mat);
            return mat;
        }

        // ---------- Noise ----------

        private static float Hash(int x, int y)
        {
            unchecked
            {
                var h = (uint)(x * 374761393 + y * 668265263);
                h = (h ^ (h >> 13)) * 1274126177u;
                return ((h ^ (h >> 16)) & 0xFFFFFF) / (float)0xFFFFFF;
            }
        }

        private static float Frac(float v) => v - Mathf.Floor(v);

        // GLSL-style smoothstep(edge0, edge1, x); Mathf.SmoothStep is an interpolation between two values instead.
        private static float Smoothstep(float e0, float e1, float x)
        {
            var t = Mathf.Clamp01((x - e0) / (e1 - e0));
            return t * t * (3f - 2f * t);
        }

        // Value noise that wraps at the texture edge: `freq` lattice cells per `size` pixels.
        private static float Noise(float x, float y, float size, float freq)
        {
            var fx = x / size * freq; var fy = y / size * freq;
            var ix = Mathf.FloorToInt(fx); var iy = Mathf.FloorToInt(fy);
            var tx = fx - ix; var ty = fy - iy;
            tx = tx * tx * (3f - 2f * tx); ty = ty * ty * (3f - 2f * ty);
            var period = Mathf.Max(1, Mathf.RoundToInt(freq));
            float V(int px, int py) => Hash(((px % period) + period) % period, ((py % period) + period) % period);
            var a = Mathf.Lerp(V(ix, iy), V(ix + 1, iy), tx);
            var b = Mathf.Lerp(V(ix, iy + 1), V(ix + 1, iy + 1), tx);
            return Mathf.Lerp(a, b, ty);
        }
    }
}
