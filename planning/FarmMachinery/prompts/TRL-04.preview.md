# TRL-04 Trailer_Header — preview prompt (Э5 → Э6)

Catalogue: TRL-04 · Prefab `FMS_Mach_Trailer_Header_Red` · no variants · 2.2×7.2×1.1 m · Generator: Sol 6.2

## Prompt

```
Stylized low-poly 3D game asset of modern farm machinery, built from chunky simplified blocks with single chamfered edges and faceted flat shading, matte colours, no textures, no gradients, no text, logos or decals. Small flat palette: signal red body #C8473B with darker red #A8372E, cream wheel rims #F2E6C9, near-black tyres #2B2D31 with large blocky tread lugs, dark grey chassis and seat #474B51, steel grey metal #8E959B, opaque blue-grey cab glass #7FA3B5. Realistic machine proportions simplified for a game, wheels clearly separate and readable, no interior, no hoses, chains, dirt or rust. Single object shown whole, three-quarter front view from about 30 degrees above, soft studio light, plain neutral light-grey background #E9E9EC, no ground, no scene, no other objects.

A single low two-axle header transport trailer (platform for carrying a combine header), EMPTY, shown whole, three-quarter view from about 30 degrees above, on a plain neutral light-grey background. Very long, narrow and low silhouette about 7.2 m long, 2.2 m wide and 1.1 m high (drawbar included in the length), with four small tyres: two axles, one near the front third and one near the rear. A steel frame in steel grey #8E959B with two chunky longitudinal rails and several cross members, painted signal red #C8473B on the outer faces of the rails (lower edges darker red #A8372E, underside #6E757B). On the frame a flat open steel deck of broad cross bars in steel grey #8E959B with dark grey #474B51 gaps. Along the deck, three chunky cradle supports (V-shaped or flat rubber-topped saddle blocks in dark grey #474B51 on red #C8473B stands), evenly spaced, that carry a long wide object, and two low side guide rails; nothing is carried, the deck is empty. Four small rubber tyres in near-black #2B2D31 with 16 sides and 12-16 large blocky tread lugs, cream wheel rims #F2E6C9 with darker cream inside #DCC9A0, wheels outside the frame with low dark grey #474B51 mudguards above them. At the front a long steel A-frame drawbar in steel grey #8E959B narrowing to one round eye (thick ring) at its tip, hanging low, pointing straight forward. Small orange #E8913A reflector blocks at the rear corners. A plain, low, sturdy transport platform.
```

## Negative

```
no ground, no scene, no shadow plane, no text, no logo, no extra objects, no people, no photorealism, no noise texture,
not cut off, no header or any load on the deck, no combine, no tractor, no tipper box, no spoked wheels
```

## Exceptions

None. The header (ATT-03) is never part of this model; it is placed in Unity on `Header_Rest`.

## Generations (filled by Codex)

| # | Changes to prompt | Seed / settings | Result |
|---|---|---|---|
| 1 | Used IMP-03 for trailer vocabulary, clarified separated axles, three saddles and empty deck | ImageGen, session model gpt-6.2-sol | Rejected: the far-side front wheel is absent where it should be visible under the open front frame (1536 x 1024 px) |
| 2 | Clarified both full-width axles and chose a more frontal view to show the far front tyre | ImageGen, session model gpt-6.2-sol | Kept: three cradles, open empty deck, two separated axles and visible matched front pair, far rear tyre occluded (1536 x 1024 px) |
