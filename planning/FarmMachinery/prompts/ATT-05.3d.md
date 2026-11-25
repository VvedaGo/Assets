# ATT-05 Header_Pickup — 3D spec (owner decision 2026-11-24)

Reference: planning/FarmMachinery/references/HRV-03.png (the pickup at the front of the forage harvester) + the current built-in `Header` of .work/models/FarmMachinery/HRV-03_ForageHarvester/build.py (geometry already accepted in review b2)

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| ~3.3 × 2.0 × 1.3 (as the built-in pickup) | 2500 | yes | no (Full) | — |

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Frame | the former HRV-03 `Header` body: red guard hood, side walls, feed intake behind the drum; add a rear adapter frame with a 1.60 × 0.90 m opening that mates with the harvester's Feeder_Front | 5, 6, 7, 8 | root at ground, centre of bbox |
| Pickup | steel drum Ø ~0.6 with chunky tine bars (as built) | 7, 8 | axis X through the drum centre |
| Feeder_Rear (empty) | centre of the rear adapter opening | — | Y 0.80, must coincide with HRV-03 / HRV-01 Feeder_Front; +Z forward |

## Anchor

ATT-03 / ATT-04 (same Feeder interface, rear adapter look), HRV-03 built-in header (shape).

## What NOT to do

- Do not change the interface numbers: opening 1.60 × 0.90 m, Feeder_Rear at Y 0.80 (same as ATT-03/ATT-04).
- No ground contact skids that push the header up; header lowest point ~0.10 m above ground when mounted.

## Fixes
