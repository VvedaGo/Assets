# HRV-01 Combine — preview prompt (Э5 → Э6)

Catalogue: HRV-01 · Комбайн зерноуборочный (`Combine`) · 3.6×8.4×4.0 m without header · 12000 tris · variants Red / Green / Blue (atlas) · pilot · Generator: Sol 6.2

Variant to render: Red (body #C8473B / #A8372E). Green and Blue are atlas swaps and are not rendered.

## Prompt

```
Stylized low-poly 3D game asset of modern farm machinery, built from chunky simplified blocks with single chamfered edges and faceted flat shading, matte colours, no textures, no gradients, no text, logos or decals. Small flat palette: signal red body #C8473B with darker red #A8372E, cream wheel rims #F2E6C9, near-black tyres #2B2D31 with large blocky tread lugs, dark grey chassis and seat #474B51, steel grey metal #8E959B, opaque blue-grey cab glass #7FA3B5. Realistic machine proportions simplified for a game, wheels clearly separate and readable, no interior, no hoses, chains, dirt or rust. Single object shown whole, three-quarter front view from about 30 degrees above, soft studio light, plain neutral light-grey background #E9E9EC, no ground, no scene, no other objects.

A single self-propelled grain combine harvester with its wide grain header mounted on the front, shown whole, three-quarter front view from about 30 degrees above, on a plain neutral light-grey background. The machine body is about 8.4 units long, 3.6 wide and 4.0 tall without the header; the header adds about 2.1 units in front and is about 6.2 units wide, much wider than the machine. Big drive wheels at the front (diameter about 1.8, wide) and smaller steering wheels at the rear (diameter about 1.1): near-black #2B2D31 tyres with large blocky tread lugs, cream #F2E6C9 rims with darker cream #DCC9A0 inner faces. Signal red #C8473B body with darker red #A8372E on lower and side faces. A closed, fully glazed four-post cab sits high at the front of the body above the inclined feeder housing: opaque blue-grey #7FA3B5 flat glass panels, red roof with a single chamfer, a small orange #E8913A beacon on the roof, a left-side door, a mirror block, pale yellow #F4E3A1 headlights. Behind and above the cab a large boxy red grain tank with a slightly sloped cover; an unloading auger tube in steel grey #8E959B lies folded along the left top edge of the tank, with a short vertical riser at its base. Rear of the machine: a boxy engine compartment with a ventilation grille block, a dark grey #474B51 exhaust pipe and a small steel grey tow hitch plate at the bottom rear. Under the cab a chunky inclined feeder housing (1.6 wide) leads forward into the header. Header: low wide red box with a cutter bar along its front edge in dark steel #6E757B, a central steel grey cross auger trough, a big eight-bladed reel in steel grey #8E959B bars on two red arms in front of the cutter bar, red crop dividers at both ends with orange #E8913A tips and orange warning stripes. Header and combine join cleanly at the feeder: same width, no gap. Signature features: the glass cab on top, the huge wide header with its reel, the folded unloading auger.
```

## Negative

```
no ground, no scene, no shadow plane, no text, no logo, no extra objects, no people, no photorealism, no noise texture,
not cut off, no grain trailer, no tractor, no crop field, no driver, no cab interior, no real brand colours or logos
```

## Exceptions

Pilot exception to "one object, no extra objects": the header ATT-03 is mounted on the combine in this preview because the prefab of HRV-01 carries it nested at Feeder_Front. The header is part of the model, not an extra object. The 3D spec of the combine itself covers only the machine without header (see HRV-01.3d.md and ATT-03.3d.md).

## Generations (filled by Codex)

| # | Changes to prompt | Seed / settings | Result |
|---|---|---|---|
| 1 | Source prompt with uniform background, faceted shading and assembly checks | ImageGen, session model gpt-6.2-sol | Rejected: auger indistinct and reel bars do not read as a continuous cage, framing too tight (1536 x 1024 px) |
| 2 | Defined reel cage, auger flights and rear wheel placement, pulled the camera back | ImageGen, session model gpt-6.2-sol | Kept: connected header, distinct reel and auger, entire assembly visible (1536 x 1024 px) |
