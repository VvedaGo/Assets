# IMP-01 Plough (`FMS_Mach_Plough`) — builder notes (Э7, 2026-11-24)

Built by Claude Opus in the owner's live Blender 5.2 via MCP (own scene `IMP-01_Plough_Build`, collection
`IMP-01_Plough` > `FMS_Mach_Plough`); source of truth `build.py` (`-- IMP-01 build|export`). Anchor: `FMS_Tractor`
shape language (preview only; no script in the repo). Geometry is written in Unity coordinates and mapped to Blender
as (-x, -z, y); the FBX export (-Z forward, Y up, baked) gives back the design coordinates in Unity.

## Decisions (coordinator answers, msg_3abec56b7aef)
1. **Beam = option B**: spec beam front (X -0.55, Z +1.05) did not reach the mast (Z 1.45–1.80) and the spec body
   points were 0.09 m off the spec beam line. Now ONE straight beam like the reference, from inside the left mast leg
   foot (X -0.47, Z +1.58) to (X +0.55, Z -1.65). Bodies on the beam line at the spec Z: X -0.208 / +0.013 / +0.234 /
   +0.455 (design coords; stagger 0.22 m/body instead of spec 0.35).
2. **Link3P_Front** exactly on the lower pin axes (lug centre); literal spec Z +1.55 dropped. Lugs X ±0.45, Y 0.60,
   pin axis X, centred at design Z 1.70 → after root re-centring (bbox design Z -1.85..+1.77, shift +0.04) the final
   `Link3P_Front` = (0, 0.60, +1.74).

## Other deviations from the spec table (reference wins for proportions)
- Mouldboards: 0.33 wide (local x -0.065..+0.265), ~0.68 long incl. share, 0.05–0.52 high, leaning-back silhouette
  (low front edge rising from the share, lifted rear edge, high rear wing) instead of 0.30 × 0.55 × 0.40. The width is
  also set so that the root bbox is symmetric in X (-0.72..+0.72), keeping Link3P_Front at X = 0 with the root at the
  bbox centre.
- Beam colours: top and upper chamfers red (5), upper half of the sides dark red (6), lower half grey (7), bottom 8 —
  the reference shows a red beam with a grey lower band (spec: sides 7).
- Beam clamps (grey blocks around the beam at each leg) added from the reference.
- Gauge wheel stub per spec (cross-arm on the beam top at Z -1.55 to a vertical plate inboard of the wheel, axle into
  the hub); the reference shows a shorter post at the beam end — kept the spec geometry (wheel X -0.62).
- Mast legs end inside the top-link bracket below the pin bore (bracket 0.24 × 0.20 × 0.14, top at Y 1.40).
- Atlas: re-exported 2026-11-24 (orchestrator note) with the shared pack atlas `T_FarmMachinery_Red_BaseColor.png` /
  material `M_FarmMachinery_Red`; geometry/UV unchanged (same fingerprint), LOD1 re-made with make_lod1.py, the
  per-item `T_FarmMachinery_IMP01_*` files deleted. All 16 atlas cells checked pixel-exact against the STYLE.md table.
- LOD1 from `make_lod1.py` is named `<Part>_Low1` as a direct root child (tool convention; PackPrefabBuilder
  re-parents it under its part and builds the LODGroup), not `<Part>_LOD1` as written in the spec.

## Rounds (reference angle: front-left ¾, ~50° off the nose, ~25° up, 70 mm)
1. Boards small/narrow, long visible legs; front beam kink (option A) visible; long wheel arm. → asked coordinator,
   enlarged boards.
2. Straight beam (B). Bodies merged into one grey wall; beam read only red on top. → leaning-back board silhouette,
   beam sides split red/grey, camera ~50°.
3. Bodies distinct, A-frame reads. Boards shorter than in the reference. → boards extended rearwards (rear rib -0.48).
4. Close to the reference; 128 px thumbnail reads (A-frame, red diagonal beam, 4 bodies, wheel). Stopped (nitpicks).

## Remaining differences vs reference
- Wheel on a long cross-arm (spec) instead of a short post at the beam end.
- Bodies overlap more in the ¾ view than in the reference (stagger 0.22 m, 70 mm lens vs the reference's stronger
  perspective); reference mouldboards look slightly larger and more curled.
- Mast legs 0.12 m (spec) look a bit slimmer than the reference A-frame.

## Checks (final)
Frame 828 tris, Wheel_Gauge 432 → 1260 / 2500 (50 %); LOD1 630 (Frame 414, Wheel 216). Size 1.44 × 1.40 × 3.62 m
(X × Y × Z). Non-manifold / loose / degenerate 0, coplanar pairs 0, component gaps 0, shares and lowest wheel lug at
Y 0. Wheel ↔ frame contact only at the axle (x -0.60..-0.42). Headless export reproduces the live model (identical
geometry fingerprint and atlas md5).
