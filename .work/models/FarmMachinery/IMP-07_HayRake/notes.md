# IMP-07 HayRake (`FMS_Mach_HayRake`) — builder notes (Э7 series batch 3, 2026-11-24)

Look rounds in the owner's live Blender (own scene/collection `IMP-07_HayRake`, removed afterwards), final export
headless (identical fingerprint to the live build). Series helpers as in batch 2 + `PART_ROT` (a part's mesh is
counter-rotated so its object gets a rotation while the world geometry stays put). Shared atlas md5 eb6768e2… unchanged.

## Layout (Unity, m; design shifted −0.605 in Z so the root is at the bbox centre) — built in Transport
- Transport bbox X ±2.28, Y 0..3.09, Z ±2.305; size 4.57 × 3.09 × 4.61. Work (arms lowered): span X 6.66 m, height 1.42 m,
  lowest tine tip 0.19 m, 0 overlaps rotor × wheels / frame (checked by rotating the arms in the build).
- `Frame` (static): steel rails X ±0.66..0.80 (Y 0.70–0.86, 3.0 long), 2 cross members, red cross cover and red gearbox
  housing (0.80 × 0.37 × 0.44, chamfered), hinge lugs flanking the arm blocks, wheel posts + axle, red A-drawbar with tip and
  the grey shared eye Ø0.24, PTO stub (Z −0.665..−0.545 shifted = spec +2.38..+2.50).
- `Arm_L` / `Arm_R` pivot (∓0.80, 0.85, −0.805) = hinge, axis Z: hinge block + pin, 0.16 arm raised 70° outward (1.58 long),
  hub post, orange reflector. Exact mirrors. Work = Blender rot Y +70° (L) / −70° (R), i.e. 70° about Unity Z.
- `Rotor_L` / `Rotor_R` (children of the arms) pivot (∓1.52, 2.184, −0.805) = hub centre: 8-sided hub Ø0.38 × 0.25, 12 tine
  arms 0.07 (every 30°, r 0.14..1.05, tilted 10° down) with orange bent tips 0.22. Local Y = disc normal (the rotor objects
  carry ±70° about Z, so spinning about local Y spins the disc; in Work local Y points straight up — verified).
- Wheels Ø0.80 × 0.28, 12 lugs: L/R (∓0.95, 0.40, −1.405).
- `Hitch_Front` (0, 0.55, +2.195) eye centre; `PTO_Front` (0, 0.70, +2.345) = Hitch + (0, 0.15, 0.15).

## Deviations from the spec / reference
- Transport width 4.57 m (spec 2.8): with the spec 70° arm angle, flat Work rotors and a 6.8 m Work span the tilted discs
  stick out; the reference Transport is even wider (≈ 4.9 m by pixel measure). Height 3.09 (spec 3.4).
- Rotor radius 1.09 (tine arms 0.91 + tips) instead of 1.10 + 0.25: keeps the Work span at 6.66 m (spec 6.8) with the rotor
  inner edge clear of the wheels; arm hinge → hub 1.50 m.
- The reference draws both rotors facing forward in Transport; with a hinge axis Z and flat rotors in Work the discs stand in
  the arm plane (normal ±X / up), so one rotor is seen nearly edge-on in the ¾ view.
- Rotor rest rotation is ±70° about Z (spec: rotation 0 in the arm frame) so that "spin axis = local Y" holds.
- Red drawbar arms (reference); tine tips orange (reference; spec slot 8).
- Hitch_Front Z +2.195 after centring the root (spec +2.80 assumed a 5.6 m long bbox; the frame is 3.0 m as specified).
- LOD1 = `make_lod1.py` `<part>_Low1` root children (CATALOG item 3), not `Rotor_*_LOD1` children.

## Rounds: 3
1. Hinge lugs coplanar with the rail bottoms, reflector overhanging the arm (gap 1.8 cm, coplanar base) → fixed.
2. Work-pose check: rotor local Y → world up, span 6.66 m, no collisions; Transport/Work check renders.
3. Live round; exported (re-import keeps the rotor rotations and positions).

## Checks (final)
Frame 360, Arm_L/R 116 each, Rotor_L/R 316 each, Wheel_L/R 432 each → 2088 / 5000 (42 %); LOD1 1044. Non-manifold / loose /
degenerate 0, coplanar 0, gaps 0. Expected contacts: arm hinge block in the rail top (pivot, ~60 pairs per side), hub post into
the rotor hub. Tyre → frame ≥ 0.010 m. FBX re-import: 17 nodes, Rotor_L/R under Arm_L/R at the design pose, points at the design
values, texture found. Headless export = live build (fingerprint identical).

## Mating (temporary copies, removed)
- On TRC-01 `Hitch_Rear`: error 0 / 0°, PTO_Front = PTO_Rear (0.0000 m), 0 overlapping face pairs, 10.0 mm.
- On TRC-02 `Hitch_Rear`: error 0, PTO 0.0000 m, 0 overlaps, 4.1 mm.

## Fix 1 (2026-11-24, review models_b3, owner decision B) — done
- The spec range 75–80° cannot meet the width target with arm 1.50 m, rotor R 1.09 m, hub drop 0.22 m and 10° tine tilt kept:
  measured Transport bbox 75° 4.18 × 3.19 m, 80° 3.78 × 3.27, 85° 3.36 × 3.33, 88° 3.10 × 3.36, 90° 2.92 × 3.38 (W × H).
  Coordinator decision (2026-11-24): **90°** — arms vertical in Transport like real rakes on the road; the V stays in Work.
- Transport (rest) bbox 2.92 × 3.38 × 4.61 m (X × Y × Z) — width ≤ 3.0 ✓, height ≤ 3.4 ✓. Work = arms lowered by 90° about Z
  (Blender rot Y +90° L / −90° R): span 6.66 m, height 1.42 m, lowest tine 0.19 m, rotor local Y → world up, 0 overlaps
  rotor × wheels / frame. Tyre → rotor ≥ 0.595 m in Transport.
- Pivots: Arm_L/R (∓0.80, 0.85, −0.805) unchanged; Rotor_L/R (∓1.02, 2.35, −0.805), rest rotation ±90° about Z (local Y = disc
  normal). Hitch_Front (0, 0.55, +2.195), PTO_Front (0, 0.70, +2.345) unchanged. Nothing else changed (tris 2088, LOD1 1044).
- Mating after the fix: TRC-01 / TRC-02 Hitch_Rear error 0, PTO 0.0000 m, 0 overlaps (10.0 / 4.1 mm).
- Exported with the fixed pack_common.export + make_lod1; re-import 17 nodes at the design values; headless = live (fingerprint).
