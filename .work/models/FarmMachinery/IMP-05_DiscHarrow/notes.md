# IMP-05 DiscHarrow (`FMS_Mach_DiscHarrow`) — builder notes (Э7 series batch 1, 2026-11-24)

No preview reference (owner decision): built from IMP-05.3d.md only, style as IMP-01/IMP-03 (drawbar eye, lug tyres, cream
rims, grey frames, red covers). Look round in the live Blender (scene/collection `IMP-05_DiscHarrow`), export headless
(same fingerprint). Preview = Transport pose from the standard series camera; Work check render
%TEMP%/farmmachinery_check/IMP-05/IMP-05_check_work.png.

## Layout (Unity, m), rest = Transport (wings folded up)
- bbox X ±1.30, Y 0..1.73, Z ±2.611.
- `Hitch_Front` (0, 0.55, +2.50) at the shared drawbar eye.
- Central frame: rails X ±0.24..0.36 (between the central discs), cross members front/mid/rear with red covers;
  two gangs: front V (outer ends back 12°) at Z 0.55, rear inverted V at Z −1.85; central sections 4 discs each
  (X ±0.15, ±0.45); discs 12-segment Ø0.70 (apothem 0.35), 0.04 thick, chamfer on the working face, bottom at Y 0.
- `Wing_L/R` hinge (∓0.80, 0.50, 0) axis Z: per gang a knuckle, axle, 4 discs (u 0.30..1.05), arm above the discs,
  hangers; longitudinal wing beam with orange tip blocks; folded 90° up. Work = Blender rot_y ±90° (L +90, R −90):
  width 4.06 m, discs on the ground, no collisions with frame/wheels.
- `Wheel_L/R` Ø0.90 × 0.30 at (∓0.70, 0.45, −0.80).

## Deviations (spec numbers are not self-consistent)
- Fold 90° about a hinge at Y 0.50 (spec ~65° at Y 0.67): with 0.70 m discs under the wing arm a 65° fold puts the
  discs ~1.6 m out (transport 3.2 m), and the spec's folded tip (±1.30, Y 2.40) implies a 5 m work width. This layout
  keeps transport 2.60 × 5.22 × 1.73 and work 4.06 m.
- Central frame 0.72 m between the rail centres (spec 1.60 W), rails placed between the discs; frame 5.22 long.
- Wing disc spacing 0.25 (spec 0.30) so the first disc clears the hinge ear when folded.
- Small hangers/struts/axles have plain 4-sided sections (budget); main arms, wing beams and gang beams are chamfered.

## Rounds: 1 (no reference to compare; checks and Work pose verified).

## Checks
Frame 1284, Wing_L/R 780 each, Wheel_L/R 432 each → 3708 / 4000 (93 %); LOD1 1854. Non-manifold/loose/degenerate 0,
coplanar 0, gaps 0. Re-import 12 nodes OK.
Mating: on TRC-01 Hitch_Rear error 0 but 25 overlapping face pairs (eye vs the shallow TRC-01 fork, same as IMP-03);
on TRC-02 Hitch_Rear error 0, 0 overlaps.
