# TRC-01 Tractor_Cab — preview prompt (Э5 → Э6)

Catalogue: TRC-01 · Tractor_Cab · Red variant (Green / Blue by atlas swap, not generated) · 2.4×4.4×3.0 m · Generator: Sol 6.2

## Prompt

```
Stylized low-poly 3D game asset of modern farm machinery, built from chunky simplified blocks with single chamfered edges and faceted flat shading, matte colours, no textures, no gradients, no text, logos or decals. Small flat palette: signal red body #C8473B with darker red #A8372E, cream wheel rims #F2E6C9, near-black tyres #2B2D31 with large blocky tread lugs, dark grey chassis and seat #474B51, steel grey metal #8E959B, opaque blue-grey cab glass #7FA3B5. Realistic machine proportions simplified for a game, wheels clearly separate and readable, no interior, no hoses, chains, dirt or rust. Single object shown whole, three-quarter front view from about 30 degrees above, soft studio light, plain neutral light-grey background #E9E9EC, no ground, no scene, no other objects.

A single medium-size farm tractor with a closed glazed cab, shown whole, three-quarter front-left view from about 30 degrees above, on a plain neutral light-grey background. Overall proportions about 2.4 m wide, 4.4 m long, 3.0 m tall. The cab is the tallest part of the silhouette: a boxy four-pillar cab set over the rear half of the machine, slightly set back from the rear wheels' front edge, with a flat roof (single chamfer on the roof edge, a small orange #E8913A beacon on the roof corner), thin red #C8473B pillars, large flat opaque blue-grey glass panels #7FA3B5 on all sides (no interior visible, glass is a solid flat colour), a cream #F2E6C9 stripe along the lower cab edge, and a small block-shaped mirror on each side. In front of the cab a long, narrow, low bonnet with a clearly chamfered top edge (one 45° bevel) in signal red #C8473B, darker red #A8372E on the side and lower faces, a dark grey #474B51 grille block on the front with a few chunky vertical bars, two pale-yellow #F4E3A1 headlight blocks at the front corners, a short vertical exhaust pipe in steel grey #8E959B standing beside the cab pillar on the bonnet, and a steel-grey front weight bar under the nose. Rear mudguards in signal red arch over the large rear wheels, with dark grey #474B51 inner mud flaps; small red front mudguards over the front wheels. A step plate in dark grey #474B51 under the left cab door.

Four separate wheels with clear gaps to the body: two smaller front wheels (diameter about 1.1 m) and two clearly larger rear wheels (diameter about 1.7 m, almost as tall as the bonnet is high plus half again). Each wheel is a near-black #2B2D31 tyre with 12 to 16 large chunky blocky tread lugs around it, and a cream #F2E6C9 rim disc with a darker cream #DCC9A0 inner face and a small hub. At the rear: a steel-grey #8E959B drawbar fork (tow hitch) low between the rear wheels, and two steel-grey lower lift arms of the three-point linkage with a dark grey #6E757B top link, plus a short steel-grey power take-off stub in the middle. The tractor sits on its four wheels with no ground.

Distinct from a simple open tractor: it must NOT be an open-seat tractor with a tall exhaust on a short bonnet and grey wheel discs; this one has an enclosed glass cab, a long chamfered bonnet and cream wheel rims.
```

## Negative

```
no ground, no scene, no shadow plane, no text, no logo, no extra objects, no people, no photorealism, no noise texture,
not cut off, no open driver seat without cab, no cab interior, no steering wheel visible, no transparent glass, no brand marks, no attached implement, no trailer
```

## Exceptions

None. Wheels, rear hitch fork and linkage belong to the model. Only the Red variant is generated; Green (#6E9F4A / #557D39) and Blue (#4A78A8 / #3A5F86) are produced by atlas swap.

## Generations (filled by Codex)

| # | Changes to prompt | Seed / settings | Result |
|---|---|---|---|
| 1 | Used HRV-01 for series style, clarified axle alignment and closed cab geometry | ImageGen, session model gpt-6.2-sol | Rejected: three mirrors and three-point linkage incorrectly placed on the side (1536 x 1024 px) |
| 2 | Specified two front-pillar mirrors and rear-centred linkage occluded in front view | ImageGen, session model gpt-6.2-sol | Kept: correct cab, two mirrors and matching tyres and rims, rear linkage occluded (1536 x 1024 px) |
