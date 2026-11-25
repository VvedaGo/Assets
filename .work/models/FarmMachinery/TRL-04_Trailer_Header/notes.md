# TRL-04 Trailer_Header (`FMS_Mach_Trailer_Header`) — builder notes (Э7 series batch 2, 2026-11-24)

Look rounds in the owner's live Blender (own scene/collection `TRL-04_Trailer_Header`), final export headless (identical
fingerprint to the last live build). Batch-2 series helpers (see TRL-01 notes). Shared atlas md5 eb6768e2…. No LOD
(catalogue), no Hitch_Rear (catalogue / spec).

## Layout (Unity, m; design shifted −0.558 in Z so the root is at the bbox centre)
- bbox X ±1.10 (tyres / mudguards), Y 0..1.02 (pad tops), Z ±3.613 (eye front / rear reflectors); length 7.23.
- `Chassis` (static): red rails X ±0.62..0.78 Y 0.44–0.60 with front/rear beams, 10 broad grey cross bars (0.22,
  open gaps), low grey side guide rails on 3 posts per side (top 0.82), 3 saddles at Z −2.958 / −0.758 / +1.442:
  red trapezoid stand + dark V pad 1.96 wide with flat plateaus at Y 1.02 (|x| 0.75–0.98) and a 5 cm V dip; axles,
  hangers, 4 dark mudguard arches with brackets; rear bumper with orange reflectors; long shared A-drawbar + cross bar
  + shared eye Ø0.24.
- Wheels Ø0.70 × 0.30, 12 lugs: FL/FR (∓0.95, 0.35, +1.642), RL/RR (∓0.95, 0.35, −3.058).
- `Hitch_Front` (0, 0.55, +3.502) eye centre.
- `Header_Rest` (0, 0.921, −0.758), rotated 90° about the vertical (Blender Z +90°; in Unity the header's +X runs along
  the trolley's +Z and its cutter bar faces −X). Y = pad top 1.02 − header lowest point 0.10 + 1 mm; Z = centre of the
  saddle span. Both headers lie on all 3 saddles (see mating).

## Deviations from the spec
- `Header_Rest` is rotated 90° about Y (spec: "+Z forward"): the 6.2 m header must lie lengthwise (catalogue), and the
  header root is placed by position AND rotation (CATALOG item 5).
- Saddle pads at 1.02 (spec ~0.95) and side guide rails top 0.82 (spec ~1.1): with rails at 1.1 the header (2.1–2.6 m
  deep, bottom at ~1.0) would cut through them; the reference shows the rails well below the saddle tops.
- Deck 1.58 wide between the wheels (spec ~2.0): wheels Ø0.70 sit outboard of the rails inside the 2.2 m width.
- Pads are 1.96 wide so that the header's lowest faces (ATT-03 cutter bar + rear wall, ATT-04 floor) rest on them.
- Tris 2648 / 2000 (132 %): the four shared pack wheels alone are 4 × 432 = 1728 (the spec guide assumed ~200 per
  wheel); the trolley itself is 920.
- Shared eye Ø0.24 (CATALOG item 6) instead of ~0.28.

## Rounds: 3
1. Coplanar beam/rail ends, deck bars floating 1 mm over the chamfered rails, axles not reaching the hubs → fixed.
2. Fewer posts, simpler mudguards (−104 tris); mudguard bracket coplanar fixed; header mating renders checked.
3. Live round; exported.

## Remaining differences vs reference
- Reference V pads are narrower (about the stand width); here they span the header footprint.

## Checks (final)
Chassis 920, 4 wheels × 432 → 2648 tris (no LOD1). Size 2.20 × 1.02 × 7.23 m. Non-manifold / loose / degenerate 0,
coplanar 0, gaps 0. Tyre → chassis ≥ 0.013 m; wheels touch only their axles. FBX re-import: 8 nodes, Hitch_Front and
Header_Rest at the design values (Header_Rest rotation kept), texture found. Headless export = live build (fingerprint).

## Mating (temporary copies, removed)
- ATT-03 root on `Header_Rest`: error 0 / 0°, lies 6.2 m along Z, lowest point 1.021 (1 mm above the pads), 0 overlaps.
- ATT-04 root on `Header_Rest`: error 0 / 0°, 5.6 m along Z, lowest point 1.021, 0 overlaps (snouts overhang ±1.30 in X).
- `Hitch_Front` on TRC-01 `Hitch_Rear`: error 0, 0 overlaps, min distance 10.0 mm.
- `Hitch_Front` on HRV-01 `Hitch_Rear`: error 0, but **10 overlapping face pairs (≈ 1 mm)**: HRV-01's hitch plate is only
  0.11 m ahead of its fork pin; the shared eye (flat at 0.111) needs ≥ 0.125 (CATALOG item 6). Fix needed in HRV-01
  (move `hitch_plate` to ≥ 0.125 ahead of the pin, like TRC-01's fix); not changed here (other item's files).

- Update 2026-11-24: the HRV-01 overlap is fixed (HRV-01 hitch plate moved to 0.125 ahead of its pin) — TRL-04 `Hitch_Front` on HRV-01 `Hitch_Rear`: error 0, 0 overlapping face pairs, 10.0 mm.
