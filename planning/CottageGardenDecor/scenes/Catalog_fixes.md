# Catalog shots: fixes (review renders_3)

## Fix 1 (2026-11-26, review renders_3) - Card.png
- Hero size: the arch is ~160 px wide (13 %) and 43 % tall in 1260x840; at 420x280 it is ~55x120 px. The island is wide and flat with
  ~35 % of its area empty grass in front (y 380-520 px of 840). Content already uses 8-62 % of the height, so the only way to enlarge
  the hero is to remove dead space, not to move it up.
  -> shrink the island: cut the front/side grass so the island is ~50 % of the width (was 63 %) and ~20 % of the height in front of
  the arch (was ~35 %); lower the camera pitch ~8 deg (less top-down, thinner island); refit so the content is 6-63 % of the height
  and the arch is >= 55 % of the height (~460 px, ~185 px wide). Bottom 37 % stays clear sky.
- Red rails (MOD edging, x 560-690 px): read as two stray red sticks leading to the gate, no meaning at card size. -> remove them or
  replace with the pack's stone path/edging in the neutral colour; keep the gnome only if it is >= 30 px tall at 1260 px (now ~25 px,
  dissolves at 420x280) - otherwise drop it or move it next to the arch.
- Clouds: keep, but the left cloud touches the top and left frame edges (cut off) -> move 30-40 px inside the frame.
- Do not change the look/sky (look v2 approved).
