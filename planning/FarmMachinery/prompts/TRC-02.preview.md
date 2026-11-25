# TRC-02 Tractor_Large — preview prompt (Э5 → Э6)

Catalogue: TRC-02 · Tractor_Large · Red variant (Green / Blue by atlas swap, not generated) · 2.9×5.8×3.5 m · Generator: Sol 6.2

## Prompt

```
Stylized low-poly 3D game asset of modern farm machinery, built from chunky simplified blocks with single chamfered edges and faceted flat shading, matte colours, no textures, no gradients, no text, logos or decals. Small flat palette: signal red body #C8473B with darker red #A8372E, cream wheel rims #F2E6C9, near-black tyres #2B2D31 with large blocky tread lugs, dark grey chassis and seat #474B51, steel grey metal #8E959B, opaque blue-grey cab glass #7FA3B5. Realistic machine proportions simplified for a game, wheels clearly separate and readable, no interior, no hoses, chains, dirt or rust. Single object shown whole, three-quarter front view from about 30 degrees above, soft studio light, plain neutral light-grey background #E9E9EC, no ground, no scene, no other objects.

A single large heavy farm tractor with four equal huge wheels and a closed glazed cab in the middle, shown whole, three-quarter front-left view from about 30 degrees above, on a plain neutral light-grey background. Overall proportions about 2.9 m wide, 5.8 m long, 3.5 m tall: a long machine, clearly bigger and longer than a medium tractor. A long, broad bonnet in signal red #C8473B with one chamfered 45° top edge, darker red #A8372E side and lower faces, a dark grey #474B51 grille block with chunky vertical bars at the front, two pale-yellow #F4E3A1 headlight blocks at the front corners and a short exhaust pipe in steel grey #8E959B beside the cab. The boxy four-pillar cab sits in the middle of the machine, flat roof with a single chamfer, opaque flat blue-grey glass #7FA3B5 on all sides (no interior visible), thin red pillars, a cream #F2E6C9 stripe along the lower cab edge, an orange #E8913A beacon on the roof and a block-shaped mirror on each side. Behind the cab a short rear deck.

Four separate wheels of the same big size (diameter about 1.9 m each, as tall as the bonnet top), one at each corner with clear gaps to the body. Each wheel is a near-black #2B2D31 tyre with 12 to 16 large chunky blocky tread lugs, a cream #F2E6C9 rim disc with darker cream #DCC9A0 inner face and a small hub. Short red mudguards above the front and rear wheels. At the front: a steel-grey #8E959B front three-point lift frame, two short lower arms and a top link in darker metal #6E757B, mounted low under the nose. At the rear: a steel-grey drawbar fork (tow hitch), two lower lift arms with a top link, and a short power take-off stub. Dark grey #474B51 chassis between the wheels and a step plate under the left cab door.

Distinct from a simple open tractor: it must NOT be an open-seat tractor with small front wheels; this is a heavy four-equal-wheels tractor with a cab and front linkage.
```

## Negative

```
no ground, no scene, no shadow plane, no text, no logo, no extra objects, no people, no photorealism, no noise texture,
not cut off, no small front wheels, no open driver seat without cab, no cab interior, no transparent glass, no brand marks, no attached implement, no trailer, no front weight block, no tracks
```

## Exceptions

None. Wheels, front and rear linkage and the rear hitch fork belong to the model. Only the Red variant is generated; Green (#6E9F4A / #557D39) and Blue (#4A78A8 / #3A5F86) are produced by atlas swap.

## Generations (filled by Codex)

| # | Changes to prompt | Seed / settings | Result |
|---|---|---|---|
| 1 | Used TRC-01 for series style, specified equal wheels, long wheelbase and front lift | ImageGen, session model gpt-6.2-sol | Rejected: far rear wheel misaligned with the rear axle and rear linkage rendered off-centre (1536 x 1024 px) |
| 2 | Switched style reference to HRV-01, clarified axle projection and occluded rear linkage | ImageGen, session model gpt-6.2-sol | Kept: long chassis, four equal-size wheels inferred from perspective and clear front lift (1536 x 1024 px) |
