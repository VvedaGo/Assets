# PRP-01 Windrow — preview prompt (Э5 → Э6)

Catalogue: PRP-01 · Валок скошенной травы, модуль 4 м (`Windrow`) · 1.4×4.0×0.4 m · 300 tris · no variants · Generator: Sol 6.2

## Prompt

```
Stylized low-poly 3D game asset of modern farm machinery, built from chunky simplified blocks with single chamfered edges and faceted flat shading, matte colours, no textures, no gradients, no text, logos or decals. Small flat palette: signal red body #C8473B with darker red #A8372E, cream wheel rims #F2E6C9, near-black tyres #2B2D31 with large blocky tread lugs, dark grey chassis and seat #474B51, steel grey metal #8E959B, opaque blue-grey cab glass #7FA3B5. Realistic machine proportions simplified for a game, wheels clearly separate and readable, no interior, no hoses, chains, dirt or rust. Single object shown whole, three-quarter front view from about 30 degrees above, soft studio light, plain neutral light-grey background #E9E9EC, no ground, no scene, no other objects.

For this prop only the machinery palette above does not apply: the object uses ONE colour, straw gold #D8B65A, with faceting alone giving the shading. A single windrow module: a straight row of cut hay lying on the ground, shown whole, three-quarter view from about 30 degrees above, on a plain neutral light-grey background. A low elongated mound about 4.0 units long, 1.4 wide and 0.4 tall, with a flat bottom and a rounded-trapezoid cross-section (wide base about 1.4, narrower ridge along the top). The ridge has a few soft chunky lumps (large flat facets, broad shallow bumps, no individual stalks) that repeat the same profile, and both short ends are closed with flat vertical faces of an identical cross-section, so that several copies line up end to end. Chunky low-poly facets, matte, a single colour, no stalks, no tufts. Signature feature: the long smooth-lumped straw mound with identical flat ends.
```

## Negative

```
no ground, no scene, no shadow plane, no text, no logo, no extra objects, no people, no photorealism, no noise texture,
not cut off, no grass blades, no individual straw stalks, no field, no soil, no tractor, no bale, no fence
```

## Exceptions

The flat bottom of the mound belongs to the model (it rests on the ground when placed). The machinery palette of the style block is not used for this prop: single colour #D8B65A (slot 15).

## Generations (filled by Codex)

| # | Changes to prompt | Seed / settings | Result |
|---|---|---|---|
| 1 | Applied the prompt exception for single straw-gold material, clarified matching flat end profiles and no fibers | ImageGen, session model gpt-6.2-sol | Kept: one low faceted straw-gold module with repeating shallow lumps and square-cut ends (1536 x 1024 px) |
