# TRL-05 GrainCart — preview prompt (Э5 → Э6)

Catalogue: TRL-05 · Prefab `FMS_Mach_GrainCart_Red` · variants Empty / Full (this preview: Empty, auger folded) · 3.6×6.8×3.6 m · Generator: Sol 6.2

## Prompt

```
Stylized low-poly 3D game asset of modern farm machinery, built from chunky simplified blocks with single chamfered edges and faceted flat shading, matte colours, no textures, no gradients, no text, logos or decals. Small flat palette: signal red body #C8473B with darker red #A8372E, cream wheel rims #F2E6C9, near-black tyres #2B2D31 with large blocky tread lugs, dark grey chassis and seat #474B51, steel grey metal #8E959B, opaque blue-grey cab glass #7FA3B5. Realistic machine proportions simplified for a game, wheels clearly separate and readable, no interior, no hoses, chains, dirt or rust. Single object shown whole, three-quarter front view from about 30 degrees above, soft studio light, plain neutral light-grey background #E9E9EC, no ground, no scene, no other objects.

A single single-axle grain cart (grain transfer hopper trailer), EMPTY, with the unloading auger folded, shown whole, three-quarter view from about 30 degrees above, on a plain neutral light-grey background. About 6.8 m long (drawbar included), 3.6 m wide across the wheels and 3.6 m high. A big trapezoid hopper in signal red #C8473B: the walls slope inward towards the bottom, wide at the top and narrower below, the front wall steep, the side walls sloping, the rim chamfered with a single 45° edge, the lower facets in darker red #A8372E, open top showing a dark red #A8372E empty floor with nothing inside. Under the hopper a chunky steel chassis in steel grey #8E959B with dark underside #6E757B and a single heavy axle. Two very large rubber tyres in near-black #2B2D31, 16 sides and large blocky tread lugs, outer diameter about 1.8 m, with cream wheel rims #F2E6C9 and darker cream inside #DCC9A0, mounted outside the hopper sides, with dark grey #474B51 half-mudguards above them, so the wheels are large and clearly separate. The unloading auger, a thick 8-sided steel tube in steel grey #8E959B with a chunky base housing, is folded: it starts at the front left lower corner of the hopper and runs diagonally upward across the front wall to a spout housing with a downward-pointing short chute above the front right corner, tube end reaching the full height of the cart. At the front a short steel drawbar in steel grey #8E959B ending in a thick round eye (ring), with a small gearbox block (PTO stub, no shaft) on the drawbar and a short chunky support foot under it. Small orange #E8913A reflector blocks at the rear corners. Sturdy heavy grain cart, no hoses, no driveshaft.
```

## Negative

```
no ground, no scene, no shadow plane, no text, no logo, no extra objects, no people, no photorealism, no noise texture,
not cut off, no grain inside, no tractor, no combine, no driveshaft, no hoses, no cab
```

## Exceptions

None. The Full variant (grain heap) is not generated here: the heap is a separate object in the 3D spec (Load_Grain, slot 15 #D8B65A).

## Generations (filled by Codex)

| # | Changes to prompt | Seed / settings | Result |
|---|---|---|---|
| 1 | Used TRL-01 for trailer style and specified single axle and folded auger on front wall | ImageGen, session model gpt-6.2-sol | Rejected: two wheels on near side and auger along long side wall (1536 x 1024 px) |
| 2 | Switched to IMP-03 for single-axle vocabulary, clarified auger across short front wall | ImageGen, session model gpt-6.2-sol | Kept: empty tapered hopper, one transverse axle with two tyres and folded diagonal front auger (1536 x 1024 px) |
