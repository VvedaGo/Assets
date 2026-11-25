# HRV-02 Baler_Round — preview prompt (Э5 → Э6)

Catalogue: HRV-02 · Пресс-подборщик рулонный (`Baler_Round`) · 2.7×4.3×2.7 m · 5000 tris · variants Closed / Open (pose) · Generator: Sol 6.2

Pose to render: Closed. No bale in the preview or in the demo (owner decision 4).

## Prompt

```
Stylized low-poly 3D game asset of modern farm machinery, built from chunky simplified blocks with single chamfered edges and faceted flat shading, matte colours, no textures, no gradients, no text, logos or decals. Small flat palette: signal red body #C8473B with darker red #A8372E, cream wheel rims #F2E6C9, near-black tyres #2B2D31 with large blocky tread lugs, dark grey chassis and seat #474B51, steel grey metal #8E959B, opaque blue-grey cab glass #7FA3B5. Realistic machine proportions simplified for a game, wheels clearly separate and readable, no interior, no hoses, chains, dirt or rust. Single object shown whole, three-quarter front view from about 30 degrees above, soft studio light, plain neutral light-grey background #E9E9EC, no ground, no scene, no other objects.

A single towed round baler (pull-type machine that makes round bales), empty and closed, shown whole, three-quarter front view from about 30 degrees above, on a plain neutral light-grey background. About 4.3 units long, 2.7 wide, 2.7 tall. The main body is a large round bale chamber: a fat drum shape about 1.8 diameter lying on its side across the machine, made of two red #C8473B 16-sided side plates with a darker red #A8372E rim and a chunky red drum shell between them with steel grey #8E959B belt roller bands, single chamfered edges. The rear half of the chamber is a separate tailgate shown closed and flush, held by a chunky hinge at the top and two simple steel grey hydraulic rods. In front of the chamber a wide pickup drum with chunky steel grey tine bars and a small red guard above it. Two large wheels (diameter about 1.0) on a single axle under the chamber, with red fenders above: near-black #2B2D31 tyres with large blocky tread lugs and cream #F2E6C9 rims. A short red-and-steel drawbar at the front ends in a steel grey eye hitch (a flat plate with a round hole) and a small support stand under it. A red cover box on the front of the chamber covers the drive. Orange #E8913A warning stripes on the sides of the tailgate. The chamber is empty and there is no bale anywhere. Signature feature: the big round drum chamber with the rear tailgate and the wide pickup.
```

## Negative

```
no ground, no scene, no shadow plane, no text, no logo, no extra objects, no people, no photorealism, no noise texture,
not cut off, no bale, no hay, no straw, no tractor, no real brand colours or logos
```

## Exceptions

None. The empty chamber and the absence of a bale are intentional (owner decision 4).

## Generations (filled by Codex)

| # | Changes to prompt | Seed / settings | Result |
|---|---|---|---|
| 1 | Used IMP-03 for series style, specified closed empty chamber, transverse drum and single axle | ImageGen, session model gpt-6.2-sol | Rejected: circular end faces forward, making the chamber longitudinal instead of transverse (1536 x 1024 px) |
| 2 | Used TRC-02 for style, aligned circular chamber side plates with the wheel rims | ImageGen, session model gpt-6.2-sol | Rejected: tow bars interfere with the pickup drum and tine sweep (1536 x 1024 px) |
| 3 | Edited second draft to route the tow bars over the pickup and attach them to the stationary front frame | ImageGen, session model gpt-6.2-sol | Kept: closed transverse chamber, clear pickup clearance, attached drawbar and support, no bale (1536 x 1024 px) |
