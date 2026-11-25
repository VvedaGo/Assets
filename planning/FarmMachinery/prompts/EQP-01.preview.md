# EQP-01 GrainAuger — preview prompt (Э5 → Э6)

Catalogue: EQP-01 · Шнековый транспортёр зерна (`GrainAuger`) · 1.6×10.5×5.0 m · 3000 tris · no variants · Generator: Sol 6.2

## Prompt

```
Stylized low-poly 3D game asset of modern farm machinery, built from chunky simplified blocks with single chamfered edges and faceted flat shading, matte colours, no textures, no gradients, no text, logos or decals. Small flat palette: signal red body #C8473B with darker red #A8372E, cream wheel rims #F2E6C9, near-black tyres #2B2D31 with large blocky tread lugs, dark grey chassis and seat #474B51, steel grey metal #8E959B, opaque blue-grey cab glass #7FA3B5. Realistic machine proportions simplified for a game, wheels clearly separate and readable, no interior, no hoses, chains, dirt or rust. Single object shown whole, three-quarter front view from about 30 degrees above, soft studio light, plain neutral light-grey background #E9E9EC, no ground, no scene, no other objects.

A single mobile grain auger conveyor (grain elevator on wheels), shown whole, three-quarter front view from about 30 degrees above, on a plain neutral light-grey background. A long straight inclined tube about 10.5 units long overall and 5.0 tall at the high end, climbing at a fixed angle of about 26 degrees, 8-sided chunky steel grey #8E959B tube (diameter about 0.5) with a few darker steel #6E757B joint bands and a short discharge hood at the top end angled downward, with orange #E8913A warning stripes on the hood. At the low end a wide chunky receiving hopper (funnel) in signal red #C8473B with darker red #A8372E sides, open on top. Under the tube a sturdy red A-frame truss support with diagonal braces and a small axle carrying two small wheels (diameter about 0.7): near-black #2B2D31 tyres with large blocky tread lugs, cream #F2E6C9 rims. A short steel grey drawbar at the low end with a steel grey eye hitch plate, and a small support foot. Chunky, no thin struts. Signature feature: the long inclined tube with the hopper at its low end.
```

## Negative

```
no ground, no scene, no shadow plane, no text, no logo, no extra objects, no people, no photorealism, no noise texture,
not cut off, no grain heap, no truck, no tractor, no building, no real brand colours or logos
```

## Exceptions

None.

## Generations (filled by Codex)

| # | Changes to prompt | Seed / settings | Result |
|---|---|---|---|
| 1 | Used IMP-03 for equipment style, specified connected hopper and axle support | ImageGen, session model gpt-6.2-sol | Rejected: undercarriage track disproportionately wide and axle reads oblique to the conveyor centerline (1536 x 1024 px) |
| 2 | Clarified 1.6 m overall wheel width, perpendicular axle and one longitudinal brace | ImageGen, session model gpt-6.2-sol | Kept: straight inclined tube, attached receiving funnel and narrow braced two-wheel frame (1536 x 1024 px) |
