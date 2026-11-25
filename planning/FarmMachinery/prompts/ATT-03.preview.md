# ATT-03 Header_Grain — preview prompt (Э5 → Э6)

Catalogue: ATT-03 · Жатка зерновая 6 м (`Header_Grain`) · 6.2×2.1×1.5 m · 5000 tris · no variants (Red; Green/Blue atlases ship) · pilot with HRV-01 · Generator: Sol 6.2

## Prompt

```
Stylized low-poly 3D game asset of modern farm machinery, built from chunky simplified blocks with single chamfered edges and faceted flat shading, matte colours, no textures, no gradients, no text, logos or decals. Small flat palette: signal red body #C8473B with darker red #A8372E, cream wheel rims #F2E6C9, near-black tyres #2B2D31 with large blocky tread lugs, dark grey chassis and seat #474B51, steel grey metal #8E959B, opaque blue-grey cab glass #7FA3B5. Realistic machine proportions simplified for a game, wheels clearly separate and readable, no interior, no hoses, chains, dirt or rust. Single object shown whole, three-quarter front view from about 30 degrees above, soft studio light, plain neutral light-grey background #E9E9EC, no ground, no scene, no other objects.

A single detachable grain harvester header (cutting platform) on its own, without any combine, shown whole, three-quarter front view from about 30 degrees above, on a plain neutral light-grey background. A very wide, low, chunky platform about 6.2 units wide, 2.1 deep and 1.5 tall including the reel. Signal red #C8473B body with darker red #A8372E on the lower and side faces. A sloped platform floor in red runs from a dark steel #6E757B cutter bar along the whole front edge (flat blocky finger points) back to a central steel grey #8E959B cross auger trough: a chunky 8-sided auger cylinder lying across the full width with simple ring flights. A tall red rear wall, and at its centre an open rectangular throat (a 1.6 wide, 0.9 high chamfered frame) leading to the machine, which should be visible only as a dark opening because the header is shown alone. A big reel in front: eight chunky steel grey bars arranged around a central axle, held by end discs, supported by two sturdy red arms rising from the rear of the platform on each side, with a central cross brace. Pointed red crop dividers at both ends with orange #E8913A tips and orange warning stripes on the end walls. Signature features: the wide shape, the big eight-bar reel above the cutter bar, the central auger. No wheels, no tractor or combine.
```

## Negative

```
no ground, no scene, no shadow plane, no text, no logo, no extra objects, no people, no photorealism, no noise texture,
not cut off, no combine, no tractor, no wheels, no crop, no wheat, no real brand colours or logos
```

## Exceptions

None. The header is shown alone (HRV-01 preview shows it mounted; this one does not).

## Generations (filled by Codex)

| # | Changes to prompt | Seed / settings | Result |
|---|---|---|---|
| 1 | Used accepted HRV-01 as geometry and palette reference, isolated header and exposed feeder throat | ImageGen, session model gpt-6.2-sol | Kept: matching reel cage, auger, cutter and divider palette, no combine (1536 x 1024 px) |
