# EQP-02 GrainBin (`FMS_Mach_GrainBin`) — builder notes (Э7 series batch 3, 2026-11-24)

Look rounds in the owner's live Blender (own scene/collection `EQP-02_GrainBin`, removed afterwards), final export
headless (identical fingerprint to the live build). Series helpers as in batch 2. Shared atlas md5 eb6768e2… unchanged.

## Layout (Unity, m; root on the ground on the bin axis)
- bbox X −3.19..+3.00 (ladder on −X), Y 0..6.00 (knob), Z ±3.00; size 6.19 × 6.00 × 6.00.
- `Body` (static): dark chamfered base ring (apothem 3.00, Y 0–0.20); 24-sided flat-faceted wall (apothem 2.90, Y 0.19–4.40,
  slot 9) with 11 vertical ribs (0.10 wide, 0.05 proud, slot 7, none on the door facet); 4 chamfered bands (0.14 tall,
  0.06 proud) at Y 2.00 / 2.80 / 3.60 / 4.25 alternating slots 7 / 8; low 24-sided cone roof (eave apothem 3.00 at Y 4.43 with
  a dark eave band, apex Y 5.78) and a 12-sided knob to Y 6.00; door frame plate (1.10 × 1.80, 0.08 proud) on the +Z facet;
  ladder on the −X facet: rails 0.08 from the ground to the eave, 8 rungs 0.06, 3 brackets into the wall, two roof rails up
  the slope to the dark hatch curb.
- `Door` pivot (−0.45, 1.05, +2.93) = left vertical edge, axis Y; panel 0.88 × 1.67 with a handle block. Rest closed.
- `Roof_Hatch` pivot (−0.75, 5.723, 0) = upper edge of the lid on the −X slope; hinge axis = Z (tangent to the roof there).
  Rest closed; opens with −70° about it without contact.

## Deviations from the spec
- **Height 6.00 instead of 7.2** (wall top 4.40, apex 5.78): the reference shows the bin wider than tall (≈ 1:1 incl. the
  roof); PIPE-04 — reference wins for proportions. Still Ø6.0, squat, grey, low cone (clearly not Farm Yard FMS_Silo).
- 4 bands (reference) instead of 5; band positions start above the door.
- Ladder and roof hatch on the **−X side** (reference: right of the door, visible in the ¾ front view); spec said +X and a
  hatch on −Z with axis X. Consequently the hatch hinge axis is Z (tangent to the roof on −X), not X.
- Root stays on the bin axis (spec); the ladder makes the bbox 0.19 m longer on −X, so the root is 0.095 m off the bbox
  centre in X.
- LOD1 = `make_lod1.py` `<part>_Low1` root children (CATALOG item 3), not `Door_LOD1` / `Roof_Hatch_LOD1` children.

## Rounds: 3
1. Spec proportions (7.2 high) read as a tall tank next to the reference; ribs coplanar with band inner faces.
2. Squatter body (reference), 4 bands, coplanar fixes (ribs / frame / base top, brackets / rails).
3. Camera matched (door centre-left, ladder on the right silhouette); live round; exported.

## Checks (final)
Body 2032, Door 24, Roof_Hatch 24 → 2080 / 3500 (59 %); LOD1 1054. Non-manifold / loose / degenerate 0, coplanar 0, gaps 0.
Door and hatch touch nothing at rest; Door open ±100° touches only the frame jamb (8–12 pairs, expected), hatch −70° 0.
FBX re-import: 7 nodes, pivots at the design values, texture found. Headless export = live build (fingerprint identical).
No mating (static building).
