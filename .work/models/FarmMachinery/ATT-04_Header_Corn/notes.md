# ATT-04 Header_Corn (`FMS_Mach_Header_Corn`) — builder notes (Э7 series batch 2, 2026-11-24)

Look rounds in the owner's live Blender (own scene/collection `ATT-04_Header_Corn`), final export headless (identical
fingerprint to the last live build). Batch-2 series helpers (see TRL-01 notes) + the ATT-03 interface frame / throat
pattern. Shared atlas md5 eb6768e2….

## Layout (Unity, m; root on the ground at the bbox centre)
- bbox X ±2.80, Y 0.10..1.30, Z ±1.299 (snout tips / interface frame face); size 5.60 × 1.20 × 2.60.
- `Frame` (one rigid mesh, no moving parts): rear wall Z −1.27..−1.13 (Y 0.10–1.05, raised centre to 1.30) with the
  throat hole 1.42 × 0.72 and a dark throat plate; interface frame 1.60 × 0.90 (outer chamfer 0.06, opening 1.40 × 0.70)
  on its back, rear face Z −1.299 (1 mm in front of the interface plane −1.30, no coplanar faces with HRV-01's frame);
  grey sloped platform (Y 0.20 at Z +0.45 → trough lip 0.42 → rear wall); 7 snout hoods at X −2.4..+2.4 (pitch 0.80),
  house-shaped section 0.45 wide / 1.00 high at the rear tapering to a blunt orange tip (0.20 long) at Z +1.30, Y ~0.2;
  6 equal row channels (0.35) with a dark gathering strip and a grey 6-sided stalk roll (Ø0.12) with 3 knobs (Ø0.20);
  static cross auger (8-sided tube Ø0.30, 8 ring flights Ø0.54, centre paddle) at (0.75, −0.70); end walls
  X ±2.63..2.785 shaped as half snouts with orange chevron, side stripe and tip.
- `Feeder_Rear` (0, 0.80, −1.30), rot 0.

## Deviations from the spec
- Auger tube Ø0.30 with flights Ø0.54 (spec "Ø ~0.55 with ring flights"): the reference shows a thin tube with big rings.
- LOD1 = `make_lod1.py` `Frame_Low1` root child (CATALOG item 3).

## Rounds: 2
1. Snouts tapered too early (narrow look), end-wall stripes not visible from the front → wider snouts, chevron on the
   end-wall slope; tip end at 1.299 so the root centre gives Feeder_Rear exactly at Z −1.30.
2. Live round + HRV-01 assembly render match the reference. Exported.

## Remaining differences vs reference
- The reference end walls are bulkier hoods merging with the outer snouts; here they are 0.155 plates beside them.

## Checks (final)
Frame 1472 / 4500 tris (33 %); LOD1 734. Non-manifold / loose / degenerate 0, coplanar 0, gaps 0, mirror X 0.
FBX re-import: 4 nodes, Feeder_Rear (0, 0.80, −1.30), texture found. Headless export = live build (fingerprint identical).

## Mating (temporary copy of HRV-01, removed)
- ATT-04 `Feeder_Rear` on HRV-01 `Feeder_Front`: error 0.000000 m / 0°, header root = Feeder_Front + (0, −0.80, +1.30)
  exactly, 0 overlapping face pairs, interface frames 1.0 mm apart. Render: %TEMP%/farmmachinery_check/ATT-04/ATT-04_mate_HRV-01.png.
- On TRL-04 `Header_Rest`: see TRL-04 notes.
