# TRC-02 Tractor_Large (`FMS_Mach_Tractor_Large`) — builder notes (Э7 series batch 1, 2026-11-24)

Look rounds in the owner's live Blender (own scene/collection `TRC-02_Tractor_Large`); final export headless (identical
geometry fingerprint to the last live round). `build.py` is assembled from the series helpers (verbatim TRC-01 helpers +
`linkage_frame`, `mate_check`, ...). Shared atlas `T_FarmMachinery_Red_BaseColor.png` / `M_FarmMachinery_Red`.

## Layout (Unity, m)
- bbox X ±1.45, Y 0..3.50 (beacon), Z ±2.94 (rear fork plates / front lower-link eyes).
- Wheels Ø1.90 × 0.65, 16 lugs 0.10: FL/FR (∓1.12, 0.95, +1.35), RL/RR (∓1.12, 0.95, −1.70); spin X, rot 0.
- Broad bonnet ±0.55 to Z 2.55 with grille, bars, corner headlights; mid cab ±0.65 (Z −1.15..+0.35), roof 3.32,
  beacon 3.50; mudguards over all four wheels; left steps, right fuel tank; exhaust right.
- `Linkage_Rear` pivot (0, 0.60, −2.20) axis X → `Link3P_Rear` (0, 0.60, −2.75); `Linkage_Front` pivot (0, 0.60, +2.40)
  → `Link3P_Front` (0, 0.60, +2.87); `PTO_Rear` (0, 0.70, −2.75); `Hitch_Rear` (0, 0.55, −2.90) on the fork pin;
  `Seat` (0, 1.80, −0.40); `Door_L` hinge (−0.64, 1.63, +0.24) axis Y.

## Deviations
- Wheel Z +1.35 / −1.70 instead of the suggested +1.75 / −1.55: the reference has the bonnet far ahead of the front axle.
- `Link3P_Front` Z +2.87 (spec ≈ +2.75): the front eyes end at +2.94 = the rear fork end, so the root stays at the bbox
  centre; bbox 5.88 m long (catalogue 5.8).
- Fork mouth deepened for the shared drawbar eye (outer Ø0.24): front plate 0.115 m ahead of the pin (Z −2.785..−2.755),
  5 mm behind the PTO stub end. TRC-01's fork is shallower (front plate 0.07 ahead of its pin): trailed implements with
  the spec eye overlap it by ~4 cm (see IMP-03/IMP-05 mating) — TRC-01 needs the same change.
- Top links touch the Body brackets, not the other linkage pieces (component gap check flags `top_link`, by design).
- Seat (0, 1.80, −0.40) instead of ≈ (0, 1.5, 0.1) (cab floor 1.62, cab Z −1.15..+0.35).

## Rounds: 4 (camera matched to the reference; wheel positions moved; mudflap clearance; fork mouth for the eye).
Remaining differences: front mudguards a bit bulkier than the reference; beacon centred on the roof.

## Checks
Body 1020, Linkage_Rear 320, Linkage_Front 320, Door_L 72, wheels 4 × 480 → 3652 / 9000 (41 %); LOD1 1826.
Non-manifold/loose/degenerate 0, coplanar 0, tyre→body ≥ 0.054 m. Re-import: 22 nodes, all points at design values.
Mating: IMP-01 on Link3P_Rear error 0, 0 overlaps (plough frame 10.5 mm from the linkage); IMP-03 and IMP-05 on
Hitch_Rear error 0, PTO_Front = PTO_Rear (IMP-03), 0 overlaps (eye 4 mm from the fork plate).
