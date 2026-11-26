# TOP-01..04 Topiary — builder notes (Э7, batch 4, 2026-11-26)

ONE registry script `build.py -- <ID> build|export|dump`. Atlas F `FMS_Garden_AtlasF.png` loaded read-only (palette
check 0 mismatches, file not rewritten), material `M_Garden_Flora`. Blender: X right, -Y front, Z up (Unity Y).
Pivot (0,0,0) = centre of the soil disc bottom. Live collections: `TOP-01_Topiary_Standard` (+ child
`TOP-01_Topiary_Standard_Rose`), `TOP-02_Topiary_Cone`, `TOP-03_Topiary_Spiral`, `TOP-04_Topiary_Tiered`.

## Shared generators
- `soil_disc`: 12-sided Ø0.50 (circumradius 0.25), 0.04 tall, slot 12, CLOSED (bottom cap added so the shell is
  manifold) -> 44 tris (spec 36 counted top + sides only).
- `stem`: 8-sided tapered prism, starts at z 0.02 inside the disc, both ends capped -> 44 tris (2 segments).
- `clipped_ball`: icosphere, every vertex pulled inward 0..0.02 (fixed seed) so the outer size stays the radius.
- `foliage_slots` / `dir_light`: two greens BY FACE DIRECTION — the face normal is binned 5x5x5 and hashed; 1 in 3
  directions (1 in 4 on the spiral band) gets the light green. Scattered facets, no band, no noise texture.
- Colours: main boxwood slot 3 `#3F6B3A`; light facets slot 0 `#6E9F4A` (spec said slot 2 `#4E7A3A`: in the render
  2 vs 3 was nearly invisible, reference light facets measure ~#668B3A, p90 green of the reference (102,139,58)).

## Deviations from the specs (reference wins, PIPE-04)
- Balls are 80-tri icospheres (bmesh subdivisions 2), not 320: the references TOP-01 and TOP-04 show big facets
  (~5 across the ball) = 80-tri geodesic; 320 rendered smooth/lumpy. TOP-04: all three balls 80 tris.
- TOP-02: cone base at z 0.30 (spec 0.20) -> 0.26 bare stem visible from the 25° view, cone 1.30 tall (reference
  measures 1.30 tall, 0.73 wide). Jitter per face column (straight edges base -> apex) instead of per ring vertex:
  per-vertex jitter kinked the faces at the ring lines, the spec asks for straight planar-looking faces.
- TOP-03: band section 5 vertices (outer face split with a 0.04 bulge; reference shows 2 facet rows on the outer face),
  outer height 0.28 / inner 0.16 (spec 0.20/0.12; reference bands ~0.29 with small gaps), outer gap 0.10..0.20,
  outer radius 0.36 -> 0.07, band starts at z 0.294 (bare trunk 0.254), trunk top 1.68 + tip 1.74 so the trunk end
  stays inside the last turn (reference: no trunk above the band). Width 0.735 x 0.668 (reference measures ~0.79).
- TOP-04: radii 0.36 / 0.26 / 0.165 (80-tri balls are inscribed smaller than the radius), centres 0.60 / 1.15 / 1.535.

## Rounds (live Blender)
1. TOP-01 live (+ TOP-02..04 headless check renders): light facets formed a horizontal cap (normal.z rule), cone stem
   hidden (0.16), cone edges kinked, spiral start flap hanging at the front right.
2. All four: direction hash colours, cone base 0.30 + column jitter, spiral start angle 150° (start cap at back left).
   Light green slot 2 too close to slot 3; spiral 0.754 wide.
3. Light facets slot 0; spiral r 0.34; TOP-04 radii up. Spiral thinner and smaller than reference, trunk tip pokes out.
4. Spiral thicker/wider (h 0.28, r 0.36), trunk tip hidden; ball light share 1 in 3. Spiral checkerboard (37 % light).
5. TOP-03 only: band light share 1 in 4 (26 %). Accepted.
128 px thumbnails: lollipop on a bare stem, cone, spiral, three balls, rose standard all read (no ground bush look).
5. (TOP-01) `_Rose`: coordinator decision 2026-11-26 option A — keep 10 rose_bloom_v2 (68 tris each), `_Rose` budget
   raised 800 -> 860 (recorded in CATALOG.md by the coordinator). Blooms tilted exactly 22° from the ball normal toward
   the viewer (0, -0.9, 0.42) (15-30° as PLT-02/03); cup base sunk 0.008 into the ball (neck -0.008), so the model is
   exactly 1.450 tall. Calyx apex inside the ball for all 10 (no WARNING). Accepted.

## Results (export live + headless reproduction, 2026-11-26)
| ID | tris (parts) | budget | size X x Y x Z, m | geometry SHA1 live = headless |
|---|---|---:|---|---|
| TOP-01 | 168 (Soil 44, Stem 44, Ball 80) | 500 | 0.576 x 0.609 x 1.391 | 87713ed2... OK (both meshes) |
| TOP-01_Rose | 848 (Soil 44, Stem 44, Ball 80, Bloom 10x68) | 860 | 0.582 x 0.609 x 1.450 | (same dump) OK |
| TOP-02 | 158 (Soil 44, Stem 44, Cone 70) | 300 | 0.678 x 0.691 x 1.600 | 986a157c... OK |
| TOP-03 | 672 (Soil 44, Trunk 62, Band 566) | 900 | 0.735 x 0.668 x 1.800 | ae70ca99... OK |
| TOP-04 | 328 (Soil 44, Stem 44, Ball1/2/3 80 each) | 600 | 0.674 x 0.692 x 1.682 | 417950e0... OK |
All: non-manifold 0, loose 0, degenerate 0, coplanar pairs 0, worst contact gap 0, min z 0.0000, pivot (0,0,0).
FBX re-import: 1 empty + 1 mesh, tris and dims identical, atlas found in `.fbm`. No LOD (catalogue). SNAP: no contract.
Spiral: 3.50 turns, 56 segments, outer gap between turns 0.099-0.204, bare trunk 0.254. Tiered: Ball1/Ball2 and
Ball2/Ball3 overlap (one solid stack), bare stem 0.21. Bare stems: TOP-01 0.76, TOP-02 0.26.
